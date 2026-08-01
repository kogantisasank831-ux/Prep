from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from document_service.api import router
from document_service.errors import (
    DocumentExtractionError,
    DocumentInfrastructureError,
    DocumentTooLargeError,
    DocumentValidationError,
    UnsupportedDocumentFormatError,
)
from document_service.models import ErrorResponse


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    correlation_id: str,
) -> JSONResponse:
    payload = ErrorResponse(
        code=code,
        message=message,
        correlation_id=correlation_id,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def create_app() -> FastAPI:
    app = FastAPI(
        title="Week 1 Document Extraction Service",
        version="0.1.0",
    )
    app.include_router(router)

    @app.exception_handler(DocumentValidationError)
    async def handle_document_validation(
        _request: Request,
        exc: DocumentValidationError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    @app.exception_handler(UnsupportedDocumentFormatError)
    async def handle_unsupported_format(
        _request: Request,
        exc: UnsupportedDocumentFormatError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    @app.exception_handler(DocumentTooLargeError)
    async def handle_document_too_large(
        _request: Request,
        exc: DocumentTooLargeError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    @app.exception_handler(DocumentExtractionError)
    async def handle_extraction_failure(
        _request: Request,
        exc: DocumentExtractionError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    @app.exception_handler(DocumentInfrastructureError)
    async def handle_infrastructure_failure(
        _request: Request,
        exc: DocumentInfrastructureError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code=exc.code,
            message=exc.message,
            correlation_id=exc.correlation_id,
        )

    return app


app = create_app()
