"""Strict contracts for Week 28 instruction tuning."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Split = Literal["train", "validation"]


class InstructionExample(BaseModel):
    """One domain instruction-response example with grouping provenance."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    example_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    category: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    response: str = Field(min_length=1)


class SFTConfig(BaseModel):
    """Data contract for response-only supervised fine-tuning batches."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    validation_modulus: int = Field(default=3, ge=2)
    max_tokens: int = Field(default=48, ge=12, le=2_048)
    batch_size: int = Field(default=2, ge=1, le=64)
    minimum_categories: int = Field(default=3, ge=1)


class PreparedExample(BaseModel):
    """Chat-template tokens and response-only loss mask."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    example_id: str
    source_id: str
    category: str
    split: Split
    instruction: str
    response: str
    tokens: tuple[str, ...]
    token_ids: tuple[int, ...]
    loss_mask: tuple[int, ...]

    @model_validator(mode="after")
    def validate_alignment(self) -> PreparedExample:
        if not (len(self.tokens) == len(self.token_ids) == len(self.loss_mask)):
            raise ValueError("prepared_fields_misaligned")
        if any(value not in (0, 1) for value in self.loss_mask):
            raise ValueError("loss_mask_invalid")
        if not any(self.loss_mask):
            raise ValueError("response_tokens_required")
        return self


class SFTBatch(BaseModel):
    """Padded batch of SFT examples."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    split: Split
    example_ids: tuple[str, ...]
    input_ids: tuple[tuple[int, ...], ...]
    attention_masks: tuple[tuple[int, ...], ...]
    loss_masks: tuple[tuple[int, ...], ...]


class InstructionManifest(BaseModel):
    """Prepared SFT data and visible quality evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    vocabulary: tuple[str, ...]
    duplicate_ids: tuple[str, ...]
    categories: tuple[str, ...]
    examples: tuple[PreparedExample, ...]
    batches: tuple[SFTBatch, ...]


class BaselineScore(BaseModel):
    """Exact-match evidence for a deliberately weak lookup baseline."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    split: Split
    total: int = Field(ge=1)
    exact_matches: int = Field(ge=0)
    exact_match_rate: float = Field(ge=0.0, le=1.0)
