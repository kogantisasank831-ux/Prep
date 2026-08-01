from typing import ClassVar


class ReaderError(Exception):
    """Base exception for the low-level reader boundary."""


class ReaderDecodingError(ReaderError):
    """The reader could not decode the resource."""


class DocumentServiceError(Exception):
    """Base exception exposed by the extraction service."""

    code: ClassVar[str] = "document_service_error"

    def __init__(self, message: str, *, correlation_id: str) -> None:
        super().__init__(message)
        self.message = message
        self.correlation_id = correlation_id


class DocumentValidationError(DocumentServiceError):
    code = "document_validation_failed"


class DocumentTooLargeError(DocumentValidationError):
    code = "document_too_large"


class UnsupportedDocumentFormatError(DocumentServiceError):
    code = "unsupported_document_format"


class DocumentExtractionError(DocumentServiceError):
    code = "document_extraction_failed"


class DocumentDecodingError(DocumentExtractionError):
    code = "document_decoding_failed"


class EmptyDocumentError(DocumentExtractionError):
    code = "empty_document"


class DocumentInfrastructureError(DocumentServiceError):
    code = "document_infrastructure_failure"
