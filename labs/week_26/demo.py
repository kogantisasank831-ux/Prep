"""CLI for the Week 26 reproducible data-pipeline lab."""

from __future__ import annotations

import argparse
import json

from labs.week_26.models import DataConfig, RawDocument
from labs.week_26.pipeline import prepare_dataset


def sample_documents() -> tuple[RawDocument, ...]:
    rows = (
        (
            "d-01",
            "manual",
            "en",
            "CC-BY-4.0",
            "Approved buyers compare price quality and delivery evidence.",
        ),
        (
            "d-02",
            "manual",
            "en",
            "CC-BY-4.0",
            "approved buyers compare price quality and delivery evidence.",
        ),
        (
            "d-03",
            "manual",
            "fr",
            "CC-BY-4.0",
            "Les acheteurs vérifient le prix et la livraison.",
        ),
        (
            "d-04",
            "manual",
            "en",
            "CC-BY-4.0",
            "Contract owners record renewal dates and accountable reviewers.",
        ),
        (
            "d-05",
            "forum",
            "en",
            "unknown",
            "This text has no approved reuse licence for training.",
        ),
        (
            "d-06",
            "synthetic",
            "en",
            "synthetic",
            "Contact buyer@example.com or +91 98765 43210 for the fictional order.",
        ),
        (
            "d-07",
            "synthetic",
            "en",
            "synthetic",
            "Invoices reconcile quantity unit price tax and approved totals.",
        ),
        (
            "d-08",
            "policy",
            "en",
            "CC-BY-4.0",
            "Write actions require explicit human approval and audit evidence.",
        ),
        (
            "d-09",
            "policy",
            "en",
            "CC-BY-4.0",
            "Retention rules define deletion ownership and review intervals.",
        ),
        (
            "d-10",
            "policy",
            "en",
            "CC-BY-4.0",
            "Policy exceptions need an owner expiry date and documented reason.",
        ),
    )
    return tuple(
        RawDocument(
            document_id=document_id,
            source=source,
            language=language,
            license_id=license_id,
            text=text,
        )
        for document_id, source, language, license_id, text in rows
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "smoke"), nargs="?", default="run")
    parser.parse_args()
    manifest = prepare_dataset(
        sample_documents(),
        DataConfig(),
        evaluation_texts=("A withheld benchmark sentence must never enter training.",),
    )
    print(json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
