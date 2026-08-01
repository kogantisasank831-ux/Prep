from fastapi.testclient import TestClient
from httpx2 import Response

from document_service.api import MAX_UPLOAD_BYTES
from document_service.main import create_app


def post_document(
    client: TestClient,
    *,
    content: bytes = b"alpha\r\nbeta",
    filename: str = "sample.txt",
    declared_media_type: str = "text/plain",
    upload_media_type: str = "text/plain",
    correlation_id: str = "endpoint-success-1",
) -> Response:
    return client.post(
        "/v1/documents/extract",
        data={
            "media_type": declared_media_type,
            "correlation_id": correlation_id,
        },
        files={"file": (filename, content, upload_media_type)},
    )


def test_extract_endpoint_success() -> None:
    with TestClient(create_app()) as client:
        response = post_document(client)

    assert response.status_code == 200
    assert response.json() == {
        "correlation_id": "endpoint-success-1",
        "media_type": "text/plain",
        "text": "alpha\nbeta",
        "character_count": len("alpha\nbeta"),
        "line_count": 2,
    }


def test_extract_endpoint_maps_unsupported_format() -> None:
    with TestClient(create_app()) as client:
        response = post_document(
            client,
            declared_media_type="application/pdf",
            upload_media_type="application/pdf",
        )

    assert response.status_code == 415
    assert response.json() == {
        "code": "unsupported_document_format",
        "message": "only text/plain documents are supported",
        "correlation_id": "endpoint-success-1",
    }


def test_extract_endpoint_rejects_mismatched_media_type() -> None:
    with TestClient(create_app()) as client:
        response = post_document(client, upload_media_type="application/octet-stream")

    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_document_format"


def test_extract_endpoint_rejects_oversized_document() -> None:
    with TestClient(create_app()) as client:
        response = post_document(client, content=b"a" * (MAX_UPLOAD_BYTES + 1))

    assert response.status_code == 413
    assert response.json() == {
        "code": "document_too_large",
        "message": "document exceeds the 1 MiB upload limit",
        "correlation_id": "endpoint-success-1",
    }


def test_extract_endpoint_rejects_invalid_request() -> None:
    with TestClient(create_app()) as client:
        response = post_document(client, correlation_id="contains space")

    assert response.status_code == 422
