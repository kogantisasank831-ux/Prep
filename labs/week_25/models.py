"""Strict contracts for the Week 25 training-loop lab."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TrainingDocument(BaseModel):
    """A small, public or synthetic document with a stable identity."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    document_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class TrainingConfig(BaseModel):
    """Reproducible hyperparameters for the dependency-free surrogate."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    epochs: int = Field(default=8, ge=1, le=100)
    learning_rate: float = Field(default=0.25, gt=0.0, le=2.0)
    warmup_steps: int = Field(default=2, ge=0)
    gradient_accumulation_steps: int = Field(default=4, ge=1)
    validation_modulus: int = Field(default=3, ge=2)
    seed: int = Field(default=25, ge=0)
    checkpoint_every: int = Field(default=2, ge=1)


class Checkpoint(BaseModel):
    """Small checkpoint metadata; weights remain internal to the lab."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    epoch: int = Field(ge=1)
    optimizer_step: int = Field(ge=1)
    train_loss: float = Field(ge=0.0)
    validation_loss: float = Field(ge=0.0)
    weights_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class TrainingRun(BaseModel):
    """Observable evidence from one training run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    seed: int = Field(ge=0)
    train_document_ids: tuple[str, ...]
    validation_document_ids: tuple[str, ...]
    vocabulary: tuple[str, ...]
    initial_train_loss: float = Field(ge=0.0)
    final_train_loss: float = Field(ge=0.0)
    validation_loss: float = Field(ge=0.0)
    optimizer_steps: int = Field(ge=1)
    learning_rates: tuple[float, ...]
    checkpoints: tuple[Checkpoint, ...]

    @model_validator(mode="after")
    def validate_partitions(self) -> TrainingRun:
        if not self.train_document_ids or not self.validation_document_ids:
            raise ValueError("train_and_validation_required")
        if set(self.train_document_ids) & set(self.validation_document_ids):
            raise ValueError("partition_overlap")
        return self
