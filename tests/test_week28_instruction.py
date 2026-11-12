"""Week 28 instruction-tuning data contracts."""

from __future__ import annotations

import subprocess
import sys

import pytest
from pydantic import ValidationError

from labs.week_28.demo import sample_examples
from labs.week_28.instruction import prepare_instruction_data, score_lookup_baseline
from labs.week_28.models import InstructionExample, SFTConfig


def test_duplicate_instruction_response_pair_is_removed() -> None:
    manifest = prepare_instruction_data(sample_examples(), SFTConfig())
    assert manifest.duplicate_ids == ("i-09",)
    assert len(manifest.examples) == 8


def test_sources_never_cross_partitions() -> None:
    manifest = prepare_instruction_data(sample_examples(), SFTConfig())
    by_source: dict[str, set[str]] = {}
    for example in manifest.examples:
        by_source.setdefault(example.source_id, set()).add(example.split)
    assert all(len(splits) == 1 for splits in by_source.values())
    assert {example.split for example in manifest.examples} == {"train", "validation"}


def test_chat_template_and_response_only_mask_align() -> None:
    manifest = prepare_instruction_data(sample_examples(), SFTConfig())
    example = manifest.examples[0]
    assistant_index = example.tokens.index("<|assistant|>")
    assert all(value == 0 for value in example.loss_mask[: assistant_index + 1])
    assert all(value == 1 for value in example.loss_mask[assistant_index + 1 :])
    assert example.tokens[-1] == "<|end|>"


def test_training_only_vocabulary_maps_validation_unknowns() -> None:
    manifest = prepare_instruction_data(sample_examples(), SFTConfig())
    unknown = manifest.vocabulary.index("<unk>")
    validation = [item for item in manifest.examples if item.split == "validation"]
    assert any(unknown in item.token_ids for item in validation)


def test_batches_are_aligned_and_padding_has_no_loss() -> None:
    manifest = prepare_instruction_data(sample_examples(), SFTConfig(batch_size=2))
    for batch in manifest.batches:
        widths = {len(row) for row in batch.input_ids}
        assert len(widths) == 1
        assert (
            len(batch.input_ids) == len(batch.attention_masks) == len(batch.loss_masks)
        )
        for attention, loss in zip(
            batch.attention_masks, batch.loss_masks, strict=True
        ):
            assert all(
                mask == 0
                for keep, mask in zip(attention, loss, strict=True)
                if keep == 0
            )


def test_lookup_baseline_exposes_memorisation_gap() -> None:
    manifest = prepare_instruction_data(sample_examples(), SFTConfig())
    train = score_lookup_baseline(manifest, "train")
    validation = score_lookup_baseline(manifest, "validation")
    assert train.exact_match_rate == 1.0
    assert validation.exact_match_rate == 0.0


def test_category_diversity_is_enforced() -> None:
    with pytest.raises(ValueError, match="insufficient_category_diversity"):
        prepare_instruction_data(sample_examples(), SFTConfig(minimum_categories=4))


def test_long_examples_are_rejected_without_silent_truncation() -> None:
    long = InstructionExample(
        example_id="long",
        source_id="source-long",
        category="qa",
        instruction=" ".join(["word"] * 50),
        response="answer",
    )
    with pytest.raises(ValueError, match="example_too_long"):
        prepare_instruction_data((*sample_examples(), long), SFTConfig(max_tokens=20))


def test_duplicate_example_id_is_rejected() -> None:
    first = sample_examples()[0]
    with pytest.raises(ValueError, match="duplicate_example_id"):
        prepare_instruction_data((first, first), SFTConfig(minimum_categories=1))


def test_strict_config_rejects_boolean_batch_size() -> None:
    with pytest.raises(ValidationError):
        SFTConfig(batch_size=True)


def test_cli_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "labs.week_28.demo", "smoke"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert '"validation_baseline"' in completed.stdout
    assert '"loss_mask"' in completed.stdout
