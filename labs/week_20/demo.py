"""Run the deterministic Week 20 reliability scenarios and smoke checks."""

from __future__ import annotations

import argparse
import json
from typing import cast

from labs.week_20.models import BatchReport, Job, Scenario
from labs.week_20.reliability import ReliableWorker


SCENARIOS: tuple[Scenario, ...] = (
    "llm-provider-outage",
    "database-timeout",
    "invalid-api-result",
    "vector-store-failure",
    "rate-limit-errors",
)


def _job(scenario: Scenario, number: int) -> Job:
    return Job(
        job_id=f"job-{number}",
        tenant_id="tenant-acme",
        idempotency_key=f"week20:{scenario}:{number}",
        scenario=scenario,
    )


def run_scenario(scenario: Scenario) -> BatchReport:
    """Run one failure simulation from fresh deterministic state."""

    return ReliableWorker().run((_job(scenario, 1),))


def run_batch() -> BatchReport:
    """Run all five jobs to demonstrate partial-batch continuation."""

    return ReliableWorker().run(
        tuple(_job(scenario, number) for number, scenario in enumerate(SCENARIOS, 1))
    )


def _smoke() -> dict[str, object]:
    checks = 0
    outage = run_scenario("llm-provider-outage").results[0]
    assert outage.status == "degraded"
    assert outage.selected_dependency == "model-secondary"
    checks += 2

    database = run_scenario("database-timeout").results[0]
    assert database.status == "degraded"
    assert database.data["freshness"] == "stale-45s"
    checks += 2

    invalid = run_scenario("invalid-api-result")
    assert invalid.results[0].status == "dead_letter"
    assert invalid.results[0].code == "invalid_response"
    checks += 2

    vector = run_scenario("vector-store-failure").results[0]
    assert vector.selected_dependency == "lexical-search"
    checks += 1

    limited = run_scenario("rate-limit-errors").results[0]
    assert limited.code == "recovered_after_retry"
    assert limited.attempts[0].scheduled_backoff_ms == 300
    checks += 2

    batch = run_batch()
    assert len(batch.results) == 5
    assert batch.completed_count == 1
    assert batch.degraded_count == 3
    assert batch.dead_letter_count == 1
    checks += 4
    assert [result.scenario for result in batch.results] == list(SCENARIOS)
    checks += 1
    assert run_batch() == run_batch()
    checks += 1
    serialized = json.dumps(batch.model_dump(mode="json"), sort_keys=True)
    assert "provider credential" not in serialized
    checks += 1
    return {"checks": checks, "scenarios": len(SCENARIOS), "status": "ok"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("case", "batch", "smoke"))
    parser.add_argument("--scenario", choices=SCENARIOS, default=SCENARIOS[0])
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "smoke":
        payload: object = _smoke()
    elif args.command == "batch":
        payload = run_batch().model_dump(mode="json")
    else:
        payload = run_scenario(cast(Scenario, args.scenario)).model_dump(mode="json")
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
