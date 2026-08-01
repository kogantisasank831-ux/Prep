import pytest
from pydantic import ValidationError

from document_service.models import DocumentRequest


def test_document_request_accepts_safe_values() -> None:
    request = DocumentRequest(
        media_type="text/plain",
        correlation_id="request-123",
    )

    assert request.media_type == "text/plain"
    assert request.correlation_id == "request-123"


@pytest.mark.parametrize(
    "correlation_id",
    ["", "contains space", "../escape", "value/segment", "a" * 65],
)
def test_document_request_rejects_unsafe_correlation_id(
    correlation_id: str,
) -> None:
    with pytest.raises(ValidationError):
        DocumentRequest(
            media_type="text/plain",
            correlation_id=correlation_id,
        )


def test_document_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        DocumentRequest.model_validate(
            {
                "media_type": "text/plain",
                "correlation_id": "request-123",
                "unexpected": "value",
            }
        )
