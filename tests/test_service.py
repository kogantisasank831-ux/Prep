import logging
from dataclasses import dataclass

import pytest

from document_service.domain import ExtractionCommand
from document_service.errors import (
    DocumentDecodingError,
    EmptyDocumentError,
    ReaderDecodingError,
    UnsupportedDocumentFormatError,
)
from document_service.service import DocumentExtractionService


@dataclass(slots=True)
class FixedReader:
    text: str

    def decode(self, content: bytes) -> str:
        return self.text


class DecodingFailingReader:
    def decode(self, content: bytes) -> str:
        raise ReaderDecodingError("simulated decode failure")


def make_command(
    *,
    filename: str = "document.txt",
    declared_media_type: str = "text/plain",
    upload_media_type: str = "text/plain",
    correlation_id: str = "request-123",
    content: bytes = b"content",
) -> ExtractionCommand:
    return ExtractionCommand(
        filename=filename,
        declared_media_type=declared_media_type,
        upload_media_type=upload_media_type,
        correlation_id=correlation_id,
        content=content,
    )


def test_service_extracts_and_normalizes_text() -> None:
    service = DocumentExtractionService(reader=FixedReader("alpha\r\nbeta\rgamma"))

    result = service.extract(make_command())

    assert result.correlation_id == "request-123"
    assert result.media_type == "text/plain"
    assert result.text == "alpha\nbeta\ngamma"
    assert result.character_count == len("alpha\nbeta\ngamma")
    assert result.line_count == 3


@pytest.mark.parametrize(
    ("filename", "declared_media_type", "upload_media_type"),
    [
        ("document.pdf", "application/pdf", "application/pdf"),
        ("document.md", "text/markdown", "text/markdown"),
        ("document.txt", "application/pdf", "application/pdf"),
        ("document.pdf", "text/plain", "text/plain"),
        ("document.txt", "text/plain", "application/octet-stream"),
    ],
)
def test_service_rejects_unsupported_formats(
    filename: str,
    declared_media_type: str,
    upload_media_type: str,
) -> None:
    service = DocumentExtractionService(reader=FixedReader("content"))

    with pytest.raises(UnsupportedDocumentFormatError):
        service.extract(
            make_command(
                filename=filename,
                declared_media_type=declared_media_type,
                upload_media_type=upload_media_type,
            )
        )


@pytest.mark.parametrize("text", ["", " ", "\n", "\t\r\n"])
def test_service_rejects_empty_or_whitespace_document(text: str) -> None:
    service = DocumentExtractionService(reader=FixedReader(text))

    with pytest.raises(EmptyDocumentError):
        service.extract(make_command())


def test_service_translates_decoding_failure() -> None:
    service = DocumentExtractionService(reader=DecodingFailingReader())

    with pytest.raises(DocumentDecodingError) as captured:
        service.extract(make_command())

    assert isinstance(captured.value.__cause__, ReaderDecodingError)


def test_service_does_not_log_document_text_or_filename(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret_text = "UNIQUE-SECRET-DOCUMENT-CONTENT"
    filename = "private-document.txt"
    service = DocumentExtractionService(reader=FixedReader(secret_text))

    with caplog.at_level(logging.INFO, logger="document_service.service"):
        result = service.extract(
            make_command(
                filename=filename,
                correlation_id="safe-correlation-123",
            )
        )

    assert result.text == secret_text
    assert secret_text not in caplog.text
    assert filename not in caplog.text
    assert all(
        getattr(record, "correlation_id", None) == "safe-correlation-123"
        for record in caplog.records
    )
