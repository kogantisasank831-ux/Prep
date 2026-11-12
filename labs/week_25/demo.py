"""CLI for the Week 25 training-foundations lab."""

from __future__ import annotations

import argparse
import json

from labs.week_25.models import TrainingConfig, TrainingDocument
from labs.week_25.training import train_causal_bigram


def sample_documents() -> tuple[TrainingDocument, ...]:
    """Return synthetic procurement sentences with stable identifiers."""

    texts = (
        "purchase orders require an approved supplier",
        "invoice totals match quantity and unit price",
        "contract reviews record owner and expiry date",
        "payment terms define the due date",
        "supplier risk reviews use verified evidence",
        "buyers compare price quality and delivery",
        "approvals precede consequential write actions",
        "audit records preserve decision provenance",
    )
    return tuple(
        TrainingDocument(document_id=f"proc-{index:02d}", text=text)
        for index, text in enumerate(texts, 1)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "smoke"), nargs="?", default="run")
    args = parser.parse_args()
    config = TrainingConfig(epochs=4 if args.command == "smoke" else 10)
    run = train_causal_bigram(sample_documents(), config)
    if not run.final_train_loss < run.initial_train_loss:
        raise SystemExit("training_loss_did_not_improve")
    print(json.dumps(run.model_dump(mode="json"), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
