"""Strict contracts for the Week 27 LoRA lab."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


Vector2 = tuple[float, float]
Matrix2 = tuple[Vector2, Vector2]


class FineTuningExample(BaseModel):
    """A two-feature teaching example."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    features: Vector2
    target: Vector2


class LoRAConfig(BaseModel):
    """LoRA hyperparameters for a frozen two-by-two base matrix."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    rank: int = Field(default=2, ge=1, le=2)
    alpha: float = Field(default=2.0, gt=0.0, le=32.0)
    learning_rate: float = Field(default=0.08, gt=0.0, le=1.0)
    epochs: int = Field(default=200, ge=1, le=2_000)
    gradient_clip_norm: float = Field(default=1.0, gt=0.0, le=100.0)
    seed: int = Field(default=27, ge=0)
    quantise_base_4bit: bool = False


class LoRARun(BaseModel):
    """Observable result from adapter-only optimisation."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    original_base: Matrix2
    effective_base: Matrix2
    adapter_a: tuple[Vector2, ...]
    adapter_b: tuple[tuple[float, ...], tuple[float, ...]]
    initial_loss: float = Field(ge=0.0)
    final_loss: float = Field(ge=0.0)
    trainable_parameters: int = Field(ge=1)
    frozen_parameters: int = Field(ge=1)
    scale: float = Field(gt=0.0)
    clipped_steps: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_rank_shapes(self) -> LoRARun:
        rank = len(self.adapter_a)
        if any(len(row) != rank for row in self.adapter_b):
            raise ValueError("adapter_rank_mismatch")
        if self.trainable_parameters != 4 * rank:
            raise ValueError("parameter_count_mismatch")
        return self
