"""CLI for the Week 28 instruction-data lab."""

from __future__ import annotations

import argparse
import json

from labs.week_28.instruction import prepare_instruction_data, score_lookup_baseline
from labs.week_28.models import InstructionExample, SFTConfig


def sample_examples() -> tuple[InstructionExample, ...]:
    rows = (
        (
            "i-01",
            "source-a",
            "classification",
            "Classify: invoice total differs from purchase order.",
            "mismatch",
        ),
        (
            "i-02",
            "source-b",
            "extraction",
            "Extract the currency from: total is INR 500.",
            '{"currency":"INR"}',
        ),
        (
            "i-03",
            "source-c",
            "qa",
            "When should a write action run?",
            "After explicit human approval.",
        ),
        (
            "i-04",
            "source-d",
            "classification",
            "Classify: supplier delivered on the agreed date.",
            "on_time",
        ),
        (
            "i-05",
            "source-e",
            "extraction",
            "Extract payment days from: net 30 terms.",
            '{"payment_days":30}',
        ),
        (
            "i-06",
            "source-f",
            "qa",
            "Why retain an audit record?",
            "To preserve decision provenance.",
        ),
        (
            "i-07",
            "source-g",
            "classification",
            "Classify: contract expiry is missing.",
            "incomplete",
        ),
        (
            "i-08",
            "source-h",
            "qa",
            "What should happen when evidence conflicts?",
            "Escalate for review.",
        ),
        (
            "i-09",
            "source-z",
            "qa",
            "what should happen when evidence conflicts?",
            "Escalate for review.",
        ),
    )
    return tuple(
        InstructionExample(
            example_id=example_id,
            source_id=source_id,
            category=category,
            instruction=instruction,
            response=response,
        )
        for example_id, source_id, category, instruction, response in rows
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("prepare", "smoke"), nargs="?", default="prepare"
    )
    parser.parse_args()
    manifest = prepare_instruction_data(sample_examples(), SFTConfig())
    payload = manifest.model_dump(mode="json")
    payload["train_baseline"] = score_lookup_baseline(manifest, "train").model_dump(
        mode="json"
    )
    payload["validation_baseline"] = score_lookup_baseline(
        manifest, "validation"
    ).model_dump(mode="json")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
