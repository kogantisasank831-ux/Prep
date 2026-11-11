"""Week 26 data-preparation contracts."""

from __future__ import annotations

import subprocess
import sys

import pytest
from pydantic import ValidationError

from labs.week_26.demo import sample_documents
from labs.week_26.models import DataConfig, RawDocument
from labs.week_26.pipeline import fingerprint, normalise, prepare_dataset


def test_normalisation_and_fingerprint_are_stable() -> None:
    assert normalise(" A  Price\n") == "a price"
    assert fingerprint(" A  Price\n") == fingerprint("a price")


def test_pipeline_rejects_license_language_duplicate_and_source_cap() -> None:
    manifest = prepare_dataset(sample_documents(), DataConfig())
    reasons = {item.document_id: item.reason for item in manifest.rejections}
    assert reasons["d-02"] == "duplicate"
    assert reasons["d-03"] == "language"
    assert reasons["d-05"] == "license"
    assert reasons["d-10"] == "source_cap"


def test_pii_is_redacted_before_sequences_are_exposed() -> None:
    manifest = prepare_dataset(sample_documents(), DataConfig())
    document = next(item for item in manifest.documents if item.document_id == "d-06")
    assert document.redaction_count == 2
    assert "buyer@example.com" not in document.text
    assert "98765" not in document.text
    assert "[EMAIL]" in document.text and "[PHONE]" in document.text


def test_contamination_is_rejected_by_fingerprint() -> None:
    benchmark = "Invoices reconcile quantity unit price tax and approved totals."
    manifest = prepare_dataset(
        sample_documents(), DataConfig(), evaluation_texts=(benchmark.lower(),)
    )
    reasons = {item.document_id: item.reason for item in manifest.rejections}
    assert reasons["d-07"] == "contamination"


def test_document_split_is_disjoint_and_has_both_partitions() -> None:
    manifest = prepare_dataset(sample_documents(), DataConfig())
    train = {item.document_id for item in manifest.documents if item.split == "train"}
    validation = {
        item.document_id for item in manifest.documents if item.split == "validation"
    }
    assert train and validation
    assert train.isdisjoint(validation)


def test_vocabulary_is_fitted_on_training_partition_only() -> None:
    manifest = prepare_dataset(sample_documents(), DataConfig())
    assert manifest.vocabulary[:4] == ("<pad>", "<bos>", "<eos>", "<unk>")
    assert all(len(sequence.token_ids) == 16 for sequence in manifest.sequences)
    assert all(len(sequence.attention_mask) == 16 for sequence in manifest.sequences)


def test_manifest_is_reproducible_and_order_independent() -> None:
    first = prepare_dataset(sample_documents(), DataConfig())
    second = prepare_dataset(tuple(reversed(sample_documents())), DataConfig())
    assert first == second


def test_config_change_updates_config_digest() -> None:
    first = prepare_dataset(sample_documents(), DataConfig(sequence_length=16))
    second = prepare_dataset(sample_documents(), DataConfig(sequence_length=20))
    assert first.config_digest != second.config_digest


def test_duplicate_identifiers_are_rejected() -> None:
    first = sample_documents()[0]
    with pytest.raises(ValueError, match="duplicate_document_id"):
        prepare_dataset((first, first), DataConfig())


def test_one_sided_accepted_split_is_rejected() -> None:
    document = RawDocument(
        document_id="one",
        source="source",
        language="en",
        license_id="synthetic",
        text="A valid synthetic teaching document has enough words.",
    )
    with pytest.raises(ValueError, match="train_and_validation"):
        prepare_dataset((document,), DataConfig())


def test_strict_config_rejects_invalid_bounds() -> None:
    with pytest.raises(ValidationError):
        DataConfig(minimum_words=10, maximum_words=5)
    with pytest.raises(ValidationError):
        DataConfig(sequence_length=True)


def test_cli_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "labs.week_26.demo", "smoke"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert '"dataset_digest"' in completed.stdout
    assert '"rejections"' in completed.stdout
