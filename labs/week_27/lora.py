"""Manual LoRA gradients over a frozen two-by-two matrix."""

from __future__ import annotations

import math
import random

from labs.week_27.models import FineTuningExample, LoRAConfig, LoRARun, Matrix2, Vector2


def quantise_symmetric_4bit(matrix: Matrix2) -> Matrix2:
    """Simulate signed 4-bit weight-only quantisation and dequantisation."""

    maximum = max(abs(value) for row in matrix for value in row)
    if maximum == 0.0:
        return matrix
    scale = maximum / 7.0
    rows: list[Vector2] = []
    for row in matrix:
        values = tuple(max(-8, min(7, round(value / scale))) * scale for value in row)
        rows.append((values[0], values[1]))
    return rows[0], rows[1]


def _forward(
    base: Matrix2,
    adapter_a: list[list[float]],
    adapter_b: list[list[float]],
    scale: float,
    features: Vector2,
) -> Vector2:
    hidden = [
        sum(row[index] * features[index] for index in range(2)) for row in adapter_a
    ]
    output: list[float] = []
    for row_index, base_row in enumerate(base):
        base_value = sum(base_row[index] * features[index] for index in range(2))
        update = sum(
            adapter_b[row_index][rank] * hidden[rank] for rank in range(len(hidden))
        )
        output.append(base_value + scale * update)
    return output[0], output[1]


def _loss(
    base: Matrix2,
    adapter_a: list[list[float]],
    adapter_b: list[list[float]],
    scale: float,
    examples: tuple[FineTuningExample, ...],
) -> float:
    total = 0.0
    for example in examples:
        prediction = _forward(base, adapter_a, adapter_b, scale, example.features)
        total += sum(
            (prediction[index] - example.target[index]) ** 2 for index in range(2)
        )
    return total / (2 * len(examples))


def train_lora(
    base: Matrix2,
    examples: tuple[FineTuningExample, ...],
    config: LoRAConfig,
) -> LoRARun:
    """Optimise only A and B while retaining the original base exactly."""

    if not examples:
        raise ValueError("examples_required")
    effective_base = (
        quantise_symmetric_4bit(base) if config.quantise_base_4bit else base
    )
    rng = random.Random(config.seed)
    adapter_a = [[rng.uniform(-0.1, 0.1) for _ in range(2)] for _ in range(config.rank)]
    adapter_b = [[0.0 for _ in range(config.rank)] for _ in range(2)]
    scale = config.alpha / config.rank
    initial_loss = _loss(effective_base, adapter_a, adapter_b, scale, examples)
    clipped_steps = 0

    for _ in range(config.epochs):
        gradient_a = [[0.0 for _ in range(2)] for _ in range(config.rank)]
        gradient_b = [[0.0 for _ in range(config.rank)] for _ in range(2)]
        for example in examples:
            hidden = [
                sum(row[index] * example.features[index] for index in range(2))
                for row in adapter_a
            ]
            prediction = _forward(
                effective_base, adapter_a, adapter_b, scale, example.features
            )
            errors = [prediction[index] - example.target[index] for index in range(2)]
            for output_index in range(2):
                for rank_index in range(config.rank):
                    gradient_b[output_index][rank_index] += (
                        scale * errors[output_index] * hidden[rank_index]
                    )
            for rank_index in range(config.rank):
                downstream = sum(
                    errors[output_index] * adapter_b[output_index][rank_index]
                    for output_index in range(2)
                )
                for input_index in range(2):
                    gradient_a[rank_index][input_index] += (
                        scale * downstream * example.features[input_index]
                    )
        count = float(len(examples))
        gradients = [
            value / count
            for matrix in (gradient_a, gradient_b)
            for row in matrix
            for value in row
        ]
        norm = math.sqrt(sum(value * value for value in gradients))
        clip_scale = min(1.0, config.gradient_clip_norm / max(norm, 1e-12))
        if clip_scale < 1.0:
            clipped_steps += 1
        for rank_index in range(config.rank):
            for input_index in range(2):
                adapter_a[rank_index][input_index] -= (
                    config.learning_rate
                    * gradient_a[rank_index][input_index]
                    / count
                    * clip_scale
                )
        for output_index in range(2):
            for rank_index in range(config.rank):
                adapter_b[output_index][rank_index] -= (
                    config.learning_rate
                    * gradient_b[output_index][rank_index]
                    / count
                    * clip_scale
                )

    return LoRARun(
        original_base=base,
        effective_base=effective_base,
        adapter_a=tuple((row[0], row[1]) for row in adapter_a),
        adapter_b=(tuple(adapter_b[0]), tuple(adapter_b[1])),
        initial_loss=initial_loss,
        final_loss=_loss(effective_base, adapter_a, adapter_b, scale, examples),
        trainable_parameters=4 * config.rank,
        frozen_parameters=4,
        scale=scale,
        clipped_steps=clipped_steps,
    )


def predict(run: LoRARun, features: Vector2) -> Vector2:
    """Run the effective frozen base plus learned adapter."""

    adapter_a = [list(row) for row in run.adapter_a]
    adapter_b = [list(row) for row in run.adapter_b]
    return _forward(run.effective_base, adapter_a, adapter_b, run.scale, features)
