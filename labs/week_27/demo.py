"""CLI for the Week 27 manual LoRA experiment."""

from __future__ import annotations

import argparse
import json

from labs.week_27.lora import predict, train_lora
from labs.week_27.models import FineTuningExample, LoRAConfig, Matrix2


BASE: Matrix2 = ((1.0, 0.0), (0.0, 1.0))


def sample_examples() -> tuple[FineTuningExample, ...]:
    return (
        FineTuningExample(features=(1.0, 0.0), target=(2.0, 0.0)),
        FineTuningExample(features=(0.0, 1.0), target=(0.0, 0.5)),
        FineTuningExample(features=(1.0, 1.0), target=(2.0, 0.5)),
        FineTuningExample(features=(-1.0, 1.0), target=(-2.0, 0.5)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "smoke"), nargs="?", default="run")
    parser.add_argument("--qlora", action="store_true")
    args = parser.parse_args()
    config = LoRAConfig(
        epochs=120 if args.command == "smoke" else 300, quantise_base_4bit=args.qlora
    )
    run = train_lora(BASE, sample_examples(), config)
    payload = run.model_dump(mode="json")
    payload["sample_prediction"] = predict(run, (1.0, 1.0))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
