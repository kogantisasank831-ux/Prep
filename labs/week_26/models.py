"""Strict contracts for the Week 26 data pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Split = Literal["train", "validation"]
RejectionReason = Literal[
    "license",
    "language",
    "quality",
    "duplicate",
    "contamination",
    "source_cap",
]


class RawDocument(BaseModel):
    """Input document with explicit provenance and use rights."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    document_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    language: str = Field(min_length=2)
    license_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class DataConfig(BaseModel):
    """Versionable cleaning, mixing and sequence policy."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    allowed_languages: tuple[str, ...] = ("en",)
    allowed_licenses: tuple[str, ...] = ("CC-BY-4.0", "synthetic")
    minimum_words: int = Field(default=5, ge=1)
    maximum_words: int = Field(default=80, ge=2)
    maximum_documents_per_source: int = Field(default=2, ge=1)
    validation_modulus: int = Field(default=3, ge=2)
    sequence_length: int = Field(default=16, ge=4, le=512)

    @model_validator(mode="after")
    def validate_ranges(self) -> DataConfig:
        if self.maximum_words < self.minimum_words:
            raise ValueError("maximum_words_before_minimum")
        if not self.allowed_languages or not self.allowed_licenses:
            raise ValueError("allowlists_required")
        return self


class CleanDocument(BaseModel):
    """Accepted and redacted document after policy gates."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    document_id: str
    source: str
    split: Split
    text: str
    redaction_count: int = Field(ge=0)
    fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")


class Rejection(BaseModel):
    """Visible reason for excluding an input document."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    document_id: str
    reason: RejectionReason


class TokenSequence(BaseModel):
    """Bounded, padded sequence with attention mask."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    document_id: str
    split: Split
    token_ids: tuple[int, ...]
    attention_mask: tuple[int, ...]

    @model_validator(mode="after")
    def validate_alignment(self) -> TokenSequence:
        if len(self.token_ids) != len(self.attention_mask):
            raise ValueError("sequence_mask_mismatch")
        if any(value not in (0, 1) for value in self.attention_mask):
            raise ValueError("attention_mask_invalid")
        return self


class DataManifest(BaseModel):
    """Reproducible output inventory."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    config_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    dataset_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    vocabulary: tuple[str, ...]
    documents: tuple[CleanDocument, ...]
    rejections: tuple[Rejection, ...]
    sequences: tuple[TokenSequence, ...]
