"""CLI for Week 30 serving estimates and experiment-report validation."""

from __future__ import annotations

import argparse
import json

from labs.week_30.models import (
    ExperimentReport,
    PackageManifest,
    ServingConfig,
    ServingObservation,
)
from labs.week_30.reporting import review_report
from labs.week_30.serving import profile_serving


def sample_config() -> ServingConfig:
    return ServingConfig(
        model_parameters_billions=3.0,
        weight_bits=4,
        gpu_memory_gib=16.0,
        non_weight_memory_gib=3.0,
        kv_bytes_per_token=131_072,
        max_context_tokens=4_096,
        requested_concurrency=8,
    )


def sample_observations() -> tuple[ServingObservation, ...]:
    return (
        ServingObservation(
            generated_tokens=512,
            duration_seconds=4.0,
            batch_size=1,
            time_to_first_token_ms=85.0,
            end_to_end_latency_ms=620.0,
        ),
        ServingObservation(
            generated_tokens=1_024,
            duration_seconds=5.0,
            batch_size=4,
            time_to_first_token_ms=110.0,
            end_to_end_latency_ms=790.0,
        ),
        ServingObservation(
            generated_tokens=2_048,
            duration_seconds=7.0,
            batch_size=8,
            time_to_first_token_ms=180.0,
            end_to_end_latency_ms=1_050.0,
        ),
        ServingObservation(
            generated_tokens=2_048,
            duration_seconds=8.0,
            batch_size=8,
            time_to_first_token_ms=240.0,
            end_to_end_latency_ms=1_280.0,
        ),
    )


def sample_report() -> ExperimentReport:
    profile = profile_serving(sample_config(), sample_observations())
    return ExperimentReport(
        objective="Compare a small domain adapter with prompted and RAG baselines on frozen procurement tasks.",
        dataset="Eight licensed synthetic teaching records split by source, with exact duplicate and contamination gates.",
        training_configuration="LoRA rank two, alpha four, response-only loss, fixed seed 27 and a bounded token batch.",
        compute_used="One local 16 GiB teaching GPU for a bounded reproducible run.",
        loss_curve=(1.8, 1.2, 0.9, 0.8),
        evaluation="Frozen exact-match and classification cases plus separate pairwise preference evidence; all values are synthetic.",
        failures=("One long structured response exceeded the first sequence limit.",),
        cost_usd=0.0,
        rag_comparison="RAG won the synthetic factual cases while the adapter improved repeated response formatting.",
        lessons_learned=(
            "Use RAG for changing facts and tuning for measured behavior gaps.",
            "Test packaging and serving assumptions on the target runtime.",
        ),
        package=PackageManifest(
            model_id="example/tiny-model",
            model_revision="revision-1",
            tokenizer_revision="tokenizer-1",
            adapter_revision="adapter-1",
            quantisation="weight-only-int4-teaching-estimate",
            runtime="vLLM-or-compatible-runtime-to-be-validated",
            model_checksum="a" * 64,
            config_checksum="b" * 64,
        ),
        serving=profile,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("capacity", "report", "smoke"), nargs="?", default="smoke"
    )
    args = parser.parse_args()
    profile = profile_serving(sample_config(), sample_observations())
    report = sample_report()
    if args.command == "capacity":
        payload: object = profile.model_dump(mode="json")
    elif args.command == "report":
        payload = report.model_dump(mode="json")
    else:
        payload = {
            "serving": profile.model_dump(mode="json"),
            "report_review": review_report(report.model_dump(mode="json")).model_dump(
                mode="json"
            ),
        }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
