"""Week 25 training-foundations contracts."""

from __future__ import annotations

import subprocess
import sys

import pytest
from pydantic import ValidationError

from labs.week_25.demo import sample_documents
from labs.week_25.models import TrainingConfig, TrainingDocument
from labs.week_25.training import (
    build_vocabulary,
    split_documents,
    tokenise,
    train_causal_bigram,
)


def test_tokenisation_is_deterministic_and_lowercase() -> None:
    assert tokenise("Price: INR 20!") == ("price", ":", "inr", "20", "!")


def test_document_split_is_stable_and_disjoint() -> None:
    first = split_documents(sample_documents(), 3)
    second = split_documents(tuple(reversed(sample_documents())), 3)
    assert {doc.document_id for doc in first[0]} == {
        doc.document_id for doc in second[0]
    }
    assert {doc.document_id for doc in first[1]} == {
        doc.document_id for doc in second[1]
    }
    assert not (
        {doc.document_id for doc in first[0]} & {doc.document_id for doc in first[1]}
    )


def test_duplicate_document_ids_are_rejected() -> None:
    document = TrainingDocument(document_id="same", text="first")
    with pytest.raises(ValueError, match="duplicate_document_id"):
        split_documents((document, document), 3)


def test_empty_partition_is_rejected() -> None:
    with pytest.raises(ValueError, match="split_requires"):
        split_documents((TrainingDocument(document_id="one", text="text"),), 3)


def test_vocabulary_is_fitted_on_train_only() -> None:
    train, validation = split_documents(sample_documents(), 3)
    vocabulary = build_vocabulary(train)
    validation_only = {
        token for document in validation for token in tokenise(document.text)
    } - {token for document in train for token in tokenise(document.text)}
    assert validation_only.isdisjoint(vocabulary)


def test_training_is_reproducible_and_reduces_training_loss() -> None:
    config = TrainingConfig(epochs=8, checkpoint_every=2)
    first = train_causal_bigram(sample_documents(), config)
    second = train_causal_bigram(sample_documents(), config)
    assert first == second
    assert first.final_train_loss < first.initial_train_loss
    assert len(first.checkpoints) == 4


def test_seed_changes_checkpoint_weights() -> None:
    first = train_causal_bigram(sample_documents(), TrainingConfig(epochs=3, seed=1))
    second = train_causal_bigram(sample_documents(), TrainingConfig(epochs=3, seed=2))
    assert first.checkpoints[-1].weights_digest != second.checkpoints[-1].weights_digest


def test_gradient_accumulation_controls_optimizer_steps() -> None:
    small = train_causal_bigram(
        sample_documents(), TrainingConfig(epochs=2, gradient_accumulation_steps=1)
    )
    large = train_causal_bigram(
        sample_documents(), TrainingConfig(epochs=2, gradient_accumulation_steps=8)
    )
    assert small.optimizer_steps > large.optimizer_steps
    assert len(small.learning_rates) == small.optimizer_steps


def test_learning_rate_warms_up_then_decays() -> None:
    run = train_causal_bigram(
        sample_documents(), TrainingConfig(epochs=3, warmup_steps=2)
    )
    assert run.learning_rates[0] < run.learning_rates[1]
    assert run.learning_rates[-1] < run.learning_rates[1]


def test_strict_config_rejects_boolean_integer() -> None:
    with pytest.raises(ValidationError):
        TrainingConfig(epochs=True)


def test_cli_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "labs.week_25.demo", "smoke"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert '"final_train_loss"' in completed.stdout
    assert '"checkpoints"' in completed.stdout
