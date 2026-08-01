import logging
from typing import ClassVar

from document_service.domain import (
    ExtractedDocument,
    ExtractionCommand,
    count_logical_lines,
    normalize_newlines,
)
from document_service.errors import (
    DocumentDecodingError,
    DocumentServiceError,
    DocumentValidationError,
    EmptyDocumentError,
    ReaderDecodingError,
    UnsupportedDocumentFormatError,
)
from document_service.ports import TextReader


logger = logging.getLogger(__name__)


class DocumentExtractionService:
    """Coordinate format policy, reading, normalization, and results."""

    supported_media_type: ClassVar[str] = "text/plain"
    supported_suffix: ClassVar[str] = ".txt"

    def __init__(self, reader: TextReader) -> None:
        self._reader = reader

    def extract(self, command: ExtractionCommand) -> ExtractedDocument:
        logger.info(
            "document_extraction_started",
            extra={
                "correlation_id": command.correlation_id,
                "media_type": command.declared_media_type,
            },
        )

        try:
            self._validate_command(command)
            raw_text = self._decode(command)
            normalized_text = normalize_newlines(raw_text)

            if normalized_text.strip() == "":
                raise EmptyDocumentError(
                    "document contains no non-whitespace text",
                    correlation_id=command.correlation_id,
                )

            result = ExtractedDocument(
                correlation_id=command.correlation_id,
                media_type=self.supported_media_type,
                text=normalized_text,
                character_count=len(normalized_text),
                line_count=count_logical_lines(normalized_text),
            )
        except DocumentServiceError as exc:
            logger.warning(
                "document_extraction_failed",
                extra={
                    "correlation_id": command.correlation_id,
                    "failure_code": exc.code,
                },
            )
            raise

        logger.info(
            "document_extraction_completed",
            extra={
                "correlation_id": result.correlation_id,
                "media_type": result.media_type,
                "character_count": result.character_count,
                "line_count": result.line_count,
            },
        )
        return result

    @classmethod
    def _validate_command(cls, command: ExtractionCommand) -> None:
        if command.correlation_id == "":
            raise DocumentValidationError(
                "correlation_id must not be empty",
                correlation_id=command.correlation_id,
            )

        if command.declared_media_type != cls.supported_media_type:
            raise UnsupportedDocumentFormatError(
                "only text/plain documents are supported",
                correlation_id=command.correlation_id,
            )

        if command.upload_media_type != command.declared_media_type:
            raise UnsupportedDocumentFormatError(
                "declared media type does not match the upload media type",
                correlation_id=command.correlation_id,
            )

        if not command.filename.lower().endswith(cls.supported_suffix):
            raise UnsupportedDocumentFormatError(
                "only .txt documents are supported",
                correlation_id=command.correlation_id,
            )

    def _decode(self, command: ExtractionCommand) -> str:
        try:
            return self._reader.decode(command.content)
        except ReaderDecodingError as exc:
            raise DocumentDecodingError(
                "document is not valid UTF-8",
                correlation_id=command.correlation_id,
            ) from exc
