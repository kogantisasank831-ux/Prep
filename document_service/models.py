import re
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from document_service.domain import ExtractedDocument


_SAFE_CORRELATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class DocumentRequest(BaseModel):
    """Untrusted JSON request boundary."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    media_type: str = Field(min_length=1, max_length=128)
    correlation_id: str = Field(min_length=1, max_length=64)

    @field_validator("media_type")
    @classmethod
    def validate_media_type_text(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("media_type must not contain surrounding whitespace")
        return value

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, value: str) -> str:
        if _SAFE_CORRELATION_ID.fullmatch(value) is None:
            raise ValueError("correlation_id contains unsupported characters")
        return value


class ExtractionResponse(BaseModel):
    """Serialized successful response boundary."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    correlation_id: str
    media_type: str
    text: str
    character_count: int = Field(ge=0)
    line_count: int = Field(ge=1)

    @classmethod
    def from_domain(cls, result: ExtractedDocument) -> Self:
        return cls(
            correlation_id=result.correlation_id,
            media_type=result.media_type,
            text=result.text,
            character_count=result.character_count,
            line_count=result.line_count,
        )


class ErrorResponse(BaseModel):
    """Stable error body owned by this application."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    code: str
    message: str
    correlation_id: str
