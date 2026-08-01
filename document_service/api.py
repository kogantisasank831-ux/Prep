from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from document_service.dependencies import get_extraction_service
from document_service.domain import ExtractionCommand
from document_service.errors import DocumentInfrastructureError, DocumentTooLargeError
from document_service.models import DocumentRequest, ExtractionResponse
from document_service.service import DocumentExtractionService


router = APIRouter(prefix="/v1/documents", tags=["documents"])
MAX_UPLOAD_BYTES = 1_048_576


def parse_document_request(
    media_type: Annotated[str, Form()],
    correlation_id: Annotated[str, Form()],
) -> DocumentRequest:
    """Validate multipart metadata with the boundary model."""
    try:
        return DocumentRequest(
            media_type=media_type,
            correlation_id=correlation_id,
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    status_code=status.HTTP_200_OK,
)
async def extract_document(
    request: Annotated[DocumentRequest, Depends(parse_document_request)],
    file: Annotated[UploadFile, File()],
    service: Annotated[
        DocumentExtractionService,
        Depends(get_extraction_service),
    ],
) -> ExtractionResponse:
    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
    except OSError as exc:
        raise DocumentInfrastructureError(
            "uploaded document could not be read",
            correlation_id=request.correlation_id,
        ) from exc

    if len(content) > MAX_UPLOAD_BYTES:
        raise DocumentTooLargeError(
            "document exceeds the 1 MiB upload limit",
            correlation_id=request.correlation_id,
        )

    command = ExtractionCommand(
        filename=file.filename or "",
        declared_media_type=request.media_type,
        upload_media_type=file.content_type or "application/octet-stream",
        correlation_id=request.correlation_id,
        content=content,
    )
    result = service.extract(command)
    return ExtractionResponse.from_domain(result)
