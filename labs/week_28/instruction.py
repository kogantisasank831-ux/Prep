"""Prepare chat-template examples and demonstrate memorisation risk."""

from __future__ import annotations

import hashlib
import re

from labs.week_28.models import (
    BaselineScore,
    InstructionExample,
    InstructionManifest,
    PreparedExample,
    SFTBatch,
    SFTConfig,
    Split,
)


TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[^\w\s]", re.IGNORECASE)
SPACE_PATTERN = re.compile(r"\s+")
RESERVED = ("<pad>", "<unk>", "<|system|>", "<|user|>", "<|assistant|>", "<|end|>")


def normalise(text: str) -> str:
    return SPACE_PATTERN.sub(" ", text).strip().lower()


def _split(source_id: str, modulus: int) -> Split:
    digest = hashlib.sha256(source_id.encode("utf-8")).digest()
    return "validation" if int.from_bytes(digest[:8], "big") % modulus == 0 else "train"


def _words(text: str) -> tuple[str, ...]:
    return tuple(token.lower() for token in TOKEN_PATTERN.findall(text))


def _templated(example: InstructionExample) -> tuple[tuple[str, ...], tuple[int, ...]]:
    prompt = (
        "<|system|>",
        "answer",
        "using",
        "the",
        "requested",
        "format",
        "<|end|>",
        "<|user|>",
        *_words(example.instruction),
        "<|end|>",
        "<|assistant|>",
    )
    response = (*_words(example.response), "<|end|>")
    return prompt + response, (0,) * len(prompt) + (1,) * len(response)


def prepare_instruction_data(
    examples: tuple[InstructionExample, ...], config: SFTConfig
) -> InstructionManifest:
    """Deduplicate, group-split, template, mask, encode and batch examples."""

    if len({example.example_id for example in examples}) != len(examples):
        raise ValueError("duplicate_example_id")
    seen: set[tuple[str, str]] = set()
    unique: list[InstructionExample] = []
    duplicate_ids: list[str] = []
    for example in sorted(examples, key=lambda item: item.example_id):
        key = (normalise(example.instruction), normalise(example.response))
        if key in seen:
            duplicate_ids.append(example.example_id)
            continue
        seen.add(key)
        unique.append(example)
    categories = tuple(sorted({example.category for example in unique}))
    if len(categories) < config.minimum_categories:
        raise ValueError("insufficient_category_diversity")
    split_by_source = {
        source_id: _split(source_id, config.validation_modulus)
        for source_id in {example.source_id for example in unique}
    }
    if set(split_by_source.values()) != {"train", "validation"}:
        raise ValueError("train_and_validation_required")

    templated = {example.example_id: _templated(example) for example in unique}
    train_tokens = sorted(
        {
            token
            for example in unique
            if split_by_source[example.source_id] == "train"
            for token in templated[example.example_id][0]
            if token not in RESERVED
        }
    )
    vocabulary = RESERVED + tuple(train_tokens)
    indexes = {token: index for index, token in enumerate(vocabulary)}
    prepared: list[PreparedExample] = []
    for example in unique:
        tokens, mask = templated[example.example_id]
        if len(tokens) > config.max_tokens:
            raise ValueError(f"example_too_long:{example.example_id}")
        token_ids = tuple(indexes.get(token, indexes["<unk>"]) for token in tokens)
        prepared.append(
            PreparedExample(
                example_id=example.example_id,
                source_id=example.source_id,
                category=example.category,
                split=split_by_source[example.source_id],
                instruction=example.instruction,
                response=example.response,
                tokens=tokens,
                token_ids=token_ids,
                loss_mask=mask,
            )
        )

    batches: list[SFTBatch] = []
    pad = indexes["<pad>"]
    for split in ("train", "validation"):
        selected = [example for example in prepared if example.split == split]
        for offset in range(0, len(selected), config.batch_size):
            members = selected[offset : offset + config.batch_size]
            width = max(len(member.token_ids) for member in members)
            inputs: list[tuple[int, ...]] = []
            attention: list[tuple[int, ...]] = []
            losses: list[tuple[int, ...]] = []
            for member in members:
                padding = width - len(member.token_ids)
                inputs.append(member.token_ids + (pad,) * padding)
                attention.append((1,) * len(member.token_ids) + (0,) * padding)
                losses.append(member.loss_mask + (0,) * padding)
            batches.append(
                SFTBatch(
                    split=split,
                    example_ids=tuple(member.example_id for member in members),
                    input_ids=tuple(inputs),
                    attention_masks=tuple(attention),
                    loss_masks=tuple(losses),
                )
            )
    return InstructionManifest(
        vocabulary=vocabulary,
        duplicate_ids=tuple(duplicate_ids),
        categories=categories,
        examples=tuple(prepared),
        batches=tuple(batches),
    )


def score_lookup_baseline(manifest: InstructionManifest, split: Split) -> BaselineScore:
    """Score an exact instruction-to-response lookup trained only on train rows."""

    lookup = {
        normalise(example.instruction): example.response
        for example in manifest.examples
        if example.split == "train"
    }
    selected = [example for example in manifest.examples if example.split == split]
    if not selected:
        raise ValueError("score_split_empty")
    matches = sum(
        lookup.get(normalise(example.instruction)) == example.response
        for example in selected
    )
    return BaselineScore(
        split=split,
        total=len(selected),
        exact_matches=matches,
        exact_match_rate=matches / len(selected),
    )
