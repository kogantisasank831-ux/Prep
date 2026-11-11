"""Week 27 LoRA contracts."""

from __future__ import annotations

import math
import subprocess
import sys

import pytest
from pydantic import ValidationError

from labs.week_27.demo import BASE, sample_examples
from labs.week_27.lora import predict, quantise_symmetric_4bit, train_lora
from labs.week_27.models import FineTuningExample, LoRAConfig


def test_adapter_training_reduces_loss() -> None:
    run = train_lora(BASE, sample_examples(), LoRAConfig(epochs=300))
    assert run.final_loss < run.initial_loss * 0.1


def test_original_base_remains_frozen() -> None:
    run = train_lora(BASE, sample_examples(), LoRAConfig(epochs=10))
    assert run.original_base == BASE
    assert BASE == ((1.0, 0.0), (0.0, 1.0))


def test_scale_and_parameter_counts_follow_rank() -> None:
    rank_one = train_lora(
        BASE, sample_examples(), LoRAConfig(rank=1, alpha=4.0, epochs=2)
    )
    rank_two = train_lora(
        BASE, sample_examples(), LoRAConfig(rank=2, alpha=4.0, epochs=2)
    )
    assert rank_one.scale == 4.0 and rank_one.trainable_parameters == 4
    assert rank_two.scale == 2.0 and rank_two.trainable_parameters == 8


def test_training_is_seed_reproducible() -> None:
    config = LoRAConfig(epochs=50, seed=7)
    assert train_lora(BASE, sample_examples(), config) == train_lora(
        BASE, sample_examples(), config
    )


def test_prediction_moves_toward_domain_target() -> None:
    run = train_lora(BASE, sample_examples(), LoRAConfig(epochs=300))
    prediction = predict(run, (1.0, 1.0))
    assert math.dist(prediction, (2.0, 0.5)) < math.dist((1.0, 1.0), (2.0, 0.5))


def test_symmetric_quantisation_is_bounded() -> None:
    quantised = quantise_symmetric_4bit(((8.0, -8.0), (1.1, 0.0)))
    assert quantised[0] == (8.0, -8.0)
    assert abs(quantised[1][0] - 1.1) < 0.1


def test_qlora_mode_uses_quantised_effective_base() -> None:
    base = ((1.0, 0.3), (-0.2, 0.9))
    run = train_lora(
        base, sample_examples(), LoRAConfig(epochs=2, quantise_base_4bit=True)
    )
    assert run.original_base == base
    assert run.effective_base == quantise_symmetric_4bit(base)


def test_empty_training_set_is_rejected() -> None:
    with pytest.raises(ValueError, match="examples_required"):
        train_lora(BASE, (), LoRAConfig())


def test_gradient_clipping_is_observable() -> None:
    extreme = (FineTuningExample(features=(100.0, 100.0), target=(-100.0, 100.0)),)
    run = train_lora(BASE, extreme, LoRAConfig(epochs=3, gradient_clip_norm=0.01))
    assert run.clipped_steps > 0


def test_strict_config_rejects_boolean_rank() -> None:
    with pytest.raises(ValidationError):
        LoRAConfig(rank=True)


def test_cli_smoke_and_qlora_smoke() -> None:
    for extra in ((), ("--qlora",)):
        completed = subprocess.run(
            [sys.executable, "-m", "labs.week_27.demo", "smoke", *extra],
            check=True,
            capture_output=True,
            text=True,
        )
        assert '"final_loss"' in completed.stdout
        assert '"sample_prediction"' in completed.stdout
