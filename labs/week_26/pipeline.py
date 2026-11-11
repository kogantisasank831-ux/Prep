"""Deterministic Week 26 cleaning, filtering, splitting and tokenisation."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import re

from labs.week_26.models import (
    CleanDocument,
    DataConfig,
    DataManifest,
    RawDocument,
    Rejection,
    RejectionReason,
    Split,
    TokenSequence,
)


EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d -]{7,}\d)(?!\d)")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[^\w\s]", re.IGNORECASE)
SPACE_PATTERN = re.compile(r"\s+")
SPECIAL_TOKENS = ("<pad>", "<bos>", "<eos>", "<unk>")


def normalise(text: str) -> str:
    """Normalise whitespace and case for exact duplicate comparison."""

    return SPACE_PATTERN.sub(" ", text).strip().lower()


def fingerprint(text: str) -> str:
    return hashlib.sha256(normalise(text).encode("utf-8")).hexdigest()


def _split(document_id: str, modulus: int) -> Split:
    digest = hashlib.sha256(document_id.encode("utf-8")).digest()
    return "validation" if int.from_bytes(digest[:8], "big") % modulus == 0 else "train"


def _redact(text: str) -> tuple[str, int]:
    text, emails = EMAIL_PATTERN.subn("[EMAIL]", text)
    text, phones = PHONE_PATTERN.subn("[PHONE]", text)
    return SPACE_PATTERN.sub(" ", text).strip(), emails + phones


def _quality_ok(text: str, config: DataConfig) -> bool:
    words = text.split()
    if not config.minimum_words <= len(words) <= config.maximum_words:
        return False
    visible = sum(character.isalnum() for character in text)
    return visible / max(len(text), 1) >= 0.5


def _config_digest(config: DataConfig) -> str:
    payload = json.dumps(
        config.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _dataset_digest(documents: list[CleanDocument]) -> str:
    payload = json.dumps(
        [document.model_dump(mode="json") for document in documents],
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def prepare_dataset(
    documents: tuple[RawDocument, ...],
    config: DataConfig,
    *,
    evaluation_texts: tuple[str, ...] = (),
) -> DataManifest:
    """Apply auditable policy gates and build fixed-length token sequences."""

    if len({document.document_id for document in documents}) != len(documents):
        raise ValueError("duplicate_document_id")
    evaluation_fingerprints = {fingerprint(text) for text in evaluation_texts}
    accepted_fingerprints: set[str] = set()
    source_counts: Counter[str] = Counter()
    clean: list[CleanDocument] = []
    rejections: list[Rejection] = []

    for document in sorted(documents, key=lambda item: item.document_id):
        reason: RejectionReason | None = None
        if document.license_id not in config.allowed_licenses:
            reason = "license"
        elif document.language not in config.allowed_languages:
            reason = "language"
        elif not _quality_ok(document.text, config):
            reason = "quality"
        else:
            document_fingerprint = fingerprint(document.text)
            if document_fingerprint in accepted_fingerprints:
                reason = "duplicate"
            elif document_fingerprint in evaluation_fingerprints:
                reason = "contamination"
            elif source_counts[document.source] >= config.maximum_documents_per_source:
                reason = "source_cap"
        if reason is not None:
            rejections.append(
                Rejection(document_id=document.document_id, reason=reason)
            )
            continue
        redacted, redaction_count = _redact(document.text)
        document_fingerprint = fingerprint(document.text)
        accepted_fingerprints.add(document_fingerprint)
        source_counts[document.source] += 1
        clean.append(
            CleanDocument(
                document_id=document.document_id,
                source=document.source,
                split=_split(document.document_id, config.validation_modulus),
                text=redacted,
                redaction_count=redaction_count,
                fingerprint=document_fingerprint,
            )
        )

    splits = {document.split for document in clean}
    if splits != {"train", "validation"}:
        raise ValueError("accepted_data_requires_train_and_validation")
    train_tokens = sorted(
        {
            token.lower()
            for clean_document in clean
            if clean_document.split == "train"
            for token in TOKEN_PATTERN.findall(clean_document.text)
        }
    )
    vocabulary = SPECIAL_TOKENS + tuple(train_tokens)
    indexes = {token: index for index, token in enumerate(vocabulary)}
    unknown = indexes["<unk>"]
    sequences: list[TokenSequence] = []
    for clean_document in clean:
        encoded = [indexes["<bos>"]]
        encoded.extend(
            indexes.get(token.lower(), unknown)
            for token in TOKEN_PATTERN.findall(clean_document.text)
        )
        encoded.append(indexes["<eos>"])
        encoded = encoded[: config.sequence_length]
        mask = [1] * len(encoded)
        padding = config.sequence_length - len(encoded)
        encoded.extend([indexes["<pad>"]] * padding)
        mask.extend([0] * padding)
        sequences.append(
            TokenSequence(
                document_id=clean_document.document_id,
                split=clean_document.split,
                token_ids=tuple(encoded),
                attention_mask=tuple(mask),
            )
        )
    return DataManifest(
        config_digest=_config_digest(config),
        dataset_digest=_dataset_digest(clean),
        vocabulary=vocabulary,
        documents=tuple(clean),
        rejections=tuple(rejections),
        sequences=tuple(sequences),
    )
