"""A transparent bigram surrogate for learning training-loop mechanics.

This module deliberately does not claim to implement a transformer.  It keeps
the objective, split, optimiser, schedule, accumulation and checkpoint state
small enough to inspect without a GPU framework.
"""

from __future__ import annotations

from collections.abc import Iterable
import hashlib
import json
import math
import random
import re

from labs.week_25.models import (
    Checkpoint,
    TrainingConfig,
    TrainingDocument,
    TrainingRun,
)


TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[^\w\s]", re.IGNORECASE)
SPECIAL_TOKENS = ("<bos>", "<eos>", "<unk>")


def tokenise(text: str) -> tuple[str, ...]:
    """Return a deterministic lowercase teaching tokenisation."""

    return tuple(TOKEN_PATTERN.findall(text.lower()))


def _bucket(document_id: str, modulus: int) -> int:
    digest = hashlib.sha256(document_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % modulus


def split_documents(
    documents: tuple[TrainingDocument, ...], modulus: int
) -> tuple[tuple[TrainingDocument, ...], tuple[TrainingDocument, ...]]:
    """Split whole documents before tokenisation to prevent overlap leakage."""

    if len({document.document_id for document in documents}) != len(documents):
        raise ValueError("duplicate_document_id")
    train = tuple(doc for doc in documents if _bucket(doc.document_id, modulus) != 0)
    validation = tuple(
        doc for doc in documents if _bucket(doc.document_id, modulus) == 0
    )
    if not train or not validation:
        raise ValueError("split_requires_train_and_validation")
    return train, validation


def build_vocabulary(documents: tuple[TrainingDocument, ...]) -> tuple[str, ...]:
    """Fit vocabulary on training documents only."""

    tokens = sorted(
        {token for document in documents for token in tokenise(document.text)}
    )
    return SPECIAL_TOKENS + tuple(tokens)


def _pairs(
    documents: Iterable[TrainingDocument], vocabulary: tuple[str, ...]
) -> tuple[tuple[int, int], ...]:
    indexes = {token: index for index, token in enumerate(vocabulary)}
    unknown = indexes["<unk>"]
    pairs: list[tuple[int, int]] = []
    for document in documents:
        encoded = [indexes["<bos>"]]
        encoded.extend(indexes.get(token, unknown) for token in tokenise(document.text))
        encoded.append(indexes["<eos>"])
        pairs.extend(zip(encoded[:-1], encoded[1:], strict=True))
    return tuple(pairs)


def _probabilities(row: list[float]) -> list[float]:
    maximum = max(row)
    exponentials = [math.exp(value - maximum) for value in row]
    total = sum(exponentials)
    return [value / total for value in exponentials]


def _loss(weights: list[list[float]], examples: tuple[tuple[int, int], ...]) -> float:
    if not examples:
        raise ValueError("examples_required")
    total = 0.0
    for source, target in examples:
        probability = max(_probabilities(weights[source])[target], 1e-12)
        total -= math.log(probability)
    return total / len(examples)


def _learning_rate(step: int, total_steps: int, config: TrainingConfig) -> float:
    if config.warmup_steps and step <= config.warmup_steps:
        return config.learning_rate * step / config.warmup_steps
    decay_steps = max(total_steps - config.warmup_steps, 1)
    elapsed = max(step - config.warmup_steps, 0)
    return config.learning_rate * max(0.05, 1.0 - elapsed / decay_steps)


def _weights_digest(weights: list[list[float]]) -> str:
    stable = [[round(value, 10) for value in row] for row in weights]
    payload = json.dumps(stable, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def train_causal_bigram(
    documents: tuple[TrainingDocument, ...], config: TrainingConfig
) -> TrainingRun:
    """Train the inspectable surrogate with SGD and gradient accumulation."""

    train_documents, validation_documents = split_documents(
        documents, config.validation_modulus
    )
    vocabulary = build_vocabulary(train_documents)
    train_pairs = _pairs(train_documents, vocabulary)
    validation_pairs = _pairs(validation_documents, vocabulary)
    rng = random.Random(config.seed)
    size = len(vocabulary)
    weights = [[rng.uniform(-0.01, 0.01) for _ in range(size)] for _ in range(size)]
    initial_loss = _loss(weights, train_pairs)
    updates_per_epoch = math.ceil(len(train_pairs) / config.gradient_accumulation_steps)
    total_steps = updates_per_epoch * config.epochs
    optimizer_step = 0
    learning_rates: list[float] = []
    checkpoints: list[Checkpoint] = []

    for epoch in range(1, config.epochs + 1):
        order = list(train_pairs)
        random.Random(config.seed + epoch).shuffle(order)
        gradients = [[0.0 for _ in range(size)] for _ in range(size)]
        accumulated = 0
        for position, (source, target) in enumerate(order, 1):
            probabilities = _probabilities(weights[source])
            for index, probability in enumerate(probabilities):
                gradients[source][index] += probability - float(index == target)
            accumulated += 1
            if accumulated == config.gradient_accumulation_steps or position == len(
                order
            ):
                optimizer_step += 1
                learning_rate = _learning_rate(optimizer_step, total_steps, config)
                learning_rates.append(learning_rate)
                for row_index in range(size):
                    for column_index in range(size):
                        weights[row_index][column_index] -= (
                            learning_rate
                            * gradients[row_index][column_index]
                            / accumulated
                        )
                        gradients[row_index][column_index] = 0.0
                accumulated = 0
        if epoch % config.checkpoint_every == 0 or epoch == config.epochs:
            checkpoints.append(
                Checkpoint(
                    epoch=epoch,
                    optimizer_step=optimizer_step,
                    train_loss=_loss(weights, train_pairs),
                    validation_loss=_loss(weights, validation_pairs),
                    weights_digest=_weights_digest(weights),
                )
            )

    return TrainingRun(
        seed=config.seed,
        train_document_ids=tuple(doc.document_id for doc in train_documents),
        validation_document_ids=tuple(doc.document_id for doc in validation_documents),
        vocabulary=vocabulary,
        initial_train_loss=initial_loss,
        final_train_loss=_loss(weights, train_pairs),
        validation_loss=_loss(weights, validation_pairs),
        optimizer_steps=optimizer_step,
        learning_rates=tuple(learning_rates),
        checkpoints=tuple(checkpoints),
    )
