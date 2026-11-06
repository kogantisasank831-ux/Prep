"""Behavior and failure-path checks for the Week 20 reliability worker."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import cast

import pytest
from pydantic import ValidationError

from labs.week_20.demo import SCENARIOS, run_batch, run_scenario
from labs.week_20.models import (
    BatchReport,
    CircuitConfig,
    DeadLetterRecord,
    DependencyName,
    DependencyResponse,
    Job,
    JobResult,
    QueueConfig,
    RetryPolicy,
    Scenario,
)
from labs.week_20.reliability import (
    CircuitBreaker,
    CircuitRegistry,
    DependencyExecutor,
    DependencyTarget,
    InMemoryWorkQueue,
    ManualClock,
    ScenarioPlan,
    ScriptedDependency,
)


def _response(
    dependency: DependencyName,
    status: str,
    *,
    elapsed_ms: int = 10,
    retry_after_ms: int | None = None,
    data: dict[str, object] | None = None,
) -> DependencyResponse:
    return DependencyResponse.model_validate(
        {
            "dependency": dependency,
            "status": status,
            "elapsed_ms": elapsed_ms,
            "data": data or {},
            "retry_after_ms": retry_after_ms,
        }
    )


def _job(
    *,
    job_id: str = "job-test",
    key: str = "key-test",
    scenario: Scenario = "rate-limit-errors",
    tenant: str = "tenant-acme",
) -> Job:
    return Job(
        job_id=job_id,
        tenant_id=tenant,
        idempotency_key=key,
        scenario=scenario,
    )


def _terminal_result(job: Job, status: str = "completed") -> JobResult:
    return JobResult.model_validate(
        {
            "job_id": job.job_id,
            "scenario": job.scenario,
            "status": status,
            "code": "ok" if status == "completed" else "invalid_response",
            "selected_dependency": "catalog-api" if status == "completed" else None,
            "data": {},
            "warnings": (),
            "attempts": (),
            "delivery_count": 1,
        }
    )


def _execute(
    responses: tuple[DependencyResponse, ...],
    *,
    policy: RetryPolicy | None = None,
    circuit: CircuitConfig | None = None,
) -> tuple[object, ManualClock]:
    dependency = responses[0].dependency
    plan = ScenarioPlan(
        "rate-limit-errors",
        (
            DependencyTarget(
                ScriptedDependency(dependency, responses), frozenset({"value"})
            ),
        ),
    )
    clock = ManualClock()
    executor = DependencyExecutor(
        clock=clock,
        retry_policy=policy or RetryPolicy(),
        circuits=CircuitRegistry(circuit or CircuitConfig()),
    )
    return executor.execute(plan), clock


def test_retry_policy_is_strict_and_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        RetryPolicy.model_validate({"max_attempts": "3"})
    with pytest.raises(ValidationError):
        RetryPolicy.model_validate({"unknown": 1})


def test_retry_policy_rejects_inverted_backoff_bounds() -> None:
    with pytest.raises(ValidationError, match="base_backoff_exceeds_cap"):
        RetryPolicy(base_backoff_ms=200, max_backoff_ms=100)


def test_rate_limit_response_requires_retry_after() -> None:
    with pytest.raises(ValidationError, match="rate_limit_requires_retry_after"):
        _response("catalog-api", "rate_limited")


def test_non_rate_limit_response_rejects_retry_after() -> None:
    with pytest.raises(ValidationError, match="retry_after_only_for_rate_limit"):
        _response("catalog-api", "ok", retry_after_ms=20)


def test_script_requires_a_matching_nonempty_response_sequence() -> None:
    with pytest.raises(ValueError, match="script_requires_response"):
        ScriptedDependency("catalog-api", ())
    with pytest.raises(ValueError, match="script_dependency_mismatch"):
        ScriptedDependency("catalog-api", (_response("supplier-api", "failed"),))


def test_manual_clock_records_virtual_waits_only() -> None:
    clock = ManualClock()
    clock.advance(25)
    clock.advance(75)
    assert clock.now_ms == 100
    assert clock.advances == (25, 75)
    with pytest.raises(ValueError, match="clock_advance_must_be_positive"):
        clock.advance(0)


def test_circuit_opens_at_threshold_and_fails_fast() -> None:
    circuit = CircuitBreaker(
        CircuitConfig(failure_threshold=2, recovery_timeout_ms=500)
    )
    circuit.record_failure(0)
    assert circuit.state == "closed"
    circuit.record_failure(10)
    assert str(circuit.state) == "open"
    assert circuit.allow_call(509) is False


def test_circuit_half_open_probe_can_close_it() -> None:
    circuit = CircuitBreaker(
        CircuitConfig(failure_threshold=1, recovery_timeout_ms=100)
    )
    circuit.record_failure(0)
    assert circuit.allow_call(100) is True
    assert circuit.state == "half_open"
    circuit.record_success()
    assert str(circuit.state) == "closed"


def test_failed_half_open_probe_reopens_circuit() -> None:
    circuit = CircuitBreaker(
        CircuitConfig(failure_threshold=1, recovery_timeout_ms=100)
    )
    circuit.record_failure(0)
    assert circuit.allow_call(100) is True
    circuit.record_failure(100)
    assert circuit.state == "open"
    assert circuit.allow_call(150) is False


def test_circuit_registry_isolates_dependency_state() -> None:
    registry = CircuitRegistry(CircuitConfig(failure_threshold=1))
    registry.for_dependency("model-primary").record_failure(0)
    assert registry.for_dependency("model-primary").state == "open"
    assert registry.for_dependency("vector-store").state == "closed"


def test_transient_failures_use_exponential_backoff_then_stop() -> None:
    resolution, clock = _execute(
        (
            _response("catalog-api", "unavailable"),
            _response("catalog-api", "unavailable"),
            _response("catalog-api", "unavailable"),
        ),
        circuit=CircuitConfig(failure_threshold=20),
    )
    assert resolution.code == "retry_exhausted"  # type: ignore[attr-defined]
    assert clock.advances == (100, 200)
    assert [row.scheduled_backoff_ms for row in resolution.attempts] == [  # type: ignore[attr-defined]
        100,
        200,
        0,
    ]


def test_backoff_is_capped() -> None:
    resolution, clock = _execute(
        tuple(_response("catalog-api", "unavailable") for _ in range(4)),
        policy=RetryPolicy(
            max_attempts=4,
            base_backoff_ms=100,
            max_backoff_ms=150,
            max_retry_after_ms=500,
            timeout_ms=100,
        ),
        circuit=CircuitConfig(failure_threshold=20),
    )
    assert resolution.status == "failed"  # type: ignore[attr-defined]
    assert clock.advances == (100, 150, 150)


def test_retry_after_is_honored_but_capped() -> None:
    resolution, clock = _execute(
        (
            _response("catalog-api", "rate_limited", retry_after_ms=5_000),
            _response("catalog-api", "ok", data={"value": 1}),
        ),
        policy=RetryPolicy(max_retry_after_ms=250),
    )
    assert resolution.code == "recovered_after_retry"  # type: ignore[attr-defined]
    assert clock.advances == (250,)


def test_llm_outage_opens_primary_and_uses_declared_model_fallback() -> None:
    result = run_scenario("llm-provider-outage").results[0]
    assert result.status == "degraded"
    assert result.code == "fallback_used"
    assert result.selected_dependency == "model-secondary"
    assert [attempt.outcome for attempt in result.attempts] == [
        "unavailable",
        "unavailable",
        "ok",
    ]
    assert result.attempts[1].circuit_state_after == "open"


def test_database_deadline_uses_bounded_stale_cache() -> None:
    result = run_scenario("database-timeout").results[0]
    assert result.status == "degraded"
    assert result.selected_dependency == "bounded-cache"
    assert result.data["freshness"] == "stale-45s"
    assert [attempt.outcome for attempt in result.attempts] == [
        "timeout",
        "timeout",
        "ok",
    ]


def test_invalid_api_contract_is_not_retried() -> None:
    report = run_scenario("invalid-api-result")
    result = report.results[0]
    assert result.status == "dead_letter"
    assert result.code == "invalid_response"
    assert len(result.attempts) == 1
    assert result.delivery_count == 1


def test_invalid_api_result_creates_minimal_dead_letter_record() -> None:
    report = run_scenario("invalid-api-result")
    record = report.dead_letters[0]
    assert record.code == "invalid_response"
    assert record.dependency_attempt_count == 1
    assert set(record.model_dump()) == {
        "job_id",
        "tenant_id",
        "scenario",
        "code",
        "delivery_count",
        "dependency_attempt_count",
    }


def test_vector_failure_uses_contract_compatible_lexical_fallback() -> None:
    result = run_scenario("vector-store-failure").results[0]
    assert result.status == "degraded"
    assert result.selected_dependency == "lexical-search"
    assert result.data == {
        "documents": ["contract-171"],
        "retrieval": "lexical",
    }


def test_rate_limit_recovers_without_fallback() -> None:
    result = run_scenario("rate-limit-errors").results[0]
    assert result.status == "completed"
    assert result.code == "recovered_after_retry"
    assert result.selected_dependency == "catalog-api"
    assert result.attempts[0].scheduled_backoff_ms == 300
    assert result.warnings == ("retry_recovered",)


def test_invalid_primary_output_can_use_an_explicit_compatible_fallback() -> None:
    primary = ScriptedDependency(
        "supplier-api", (_response("supplier-api", "ok", data={"wrong": 1}),)
    )
    fallback = ScriptedDependency(
        "bounded-cache",
        (_response("bounded-cache", "ok", data={"value": "cached"}),),
    )
    plan = ScenarioPlan(
        "invalid-api-result",
        (
            DependencyTarget(primary, frozenset({"value"})),
            DependencyTarget(fallback, frozenset({"value"})),
        ),
    )
    executor = DependencyExecutor(
        clock=ManualClock(),
        retry_policy=RetryPolicy(),
        circuits=CircuitRegistry(CircuitConfig()),
    )
    resolution = executor.execute(plan)
    assert resolution.status == "degraded"
    assert resolution.selected_dependency == "bounded-cache"


def test_open_circuit_skips_invocation_and_moves_to_fallback() -> None:
    registry = CircuitRegistry(CircuitConfig(failure_threshold=1))
    registry.for_dependency("model-primary").record_failure(0)
    primary = ScriptedDependency(
        "model-primary",
        (_response("model-primary", "ok", data={"value": "unused"}),),
    )
    fallback = ScriptedDependency(
        "model-secondary",
        (_response("model-secondary", "ok", data={"value": "safe"}),),
    )
    plan = ScenarioPlan(
        "llm-provider-outage",
        (
            DependencyTarget(primary, frozenset({"value"})),
            DependencyTarget(fallback, frozenset({"value"})),
        ),
    )
    resolution = DependencyExecutor(
        clock=ManualClock(), retry_policy=RetryPolicy(), circuits=registry
    ).execute(plan)
    assert primary.call_count == 0
    assert resolution.attempts[0].outcome == "circuit_open"
    assert resolution.selected_dependency == "model-secondary"


def test_batch_preserves_input_order_and_all_terminal_results() -> None:
    report = run_batch()
    assert [result.scenario for result in report.results] == list(SCENARIOS)
    assert len(report.results) == 5
    assert report.completed_count == 1
    assert report.degraded_count == 3
    assert report.dead_letter_count == 1


def test_one_permanent_failure_does_not_abort_later_jobs() -> None:
    report = run_batch()
    invalid_index = list(SCENARIOS).index("invalid-api-result")
    assert report.results[invalid_index].status == "dead_letter"
    assert report.results[invalid_index + 1].status == "degraded"
    assert report.results[invalid_index + 2].status == "completed"


def test_batch_is_deterministic() -> None:
    assert run_batch() == run_batch()


def test_queue_suppresses_same_idempotency_key_and_exposes_cached_result() -> None:
    queue = InMemoryWorkQueue(QueueConfig())
    job = _job()
    assert queue.submit(job) is True
    leased = queue.lease()
    assert leased == job
    result = _terminal_result(job)
    queue.ack(job, result)
    replay = _job(job_id="job-replay")
    assert queue.submit(replay) is False
    assert queue.result_for(job.idempotency_key) == result


def test_queue_rejects_idempotency_key_reuse_for_different_work() -> None:
    queue = InMemoryWorkQueue(QueueConfig())
    queue.submit(_job())
    with pytest.raises(ValueError, match="idempotency_key_conflict"):
        queue.submit(_job(job_id="job-other", scenario="database-timeout"))
    with pytest.raises(ValueError, match="idempotency_key_conflict"):
        queue.submit(_job(job_id="job-other", tenant="tenant-rival"))


def test_queue_rejects_duplicate_job_ids_even_before_lease() -> None:
    queue = InMemoryWorkQueue(QueueConfig())
    queue.submit(_job())
    with pytest.raises(ValueError, match="duplicate_job_id"):
        queue.submit(_job(key="key-other"))


def test_queue_requires_a_lease_before_ack_or_requeue() -> None:
    queue = InMemoryWorkQueue(QueueConfig())
    job = _job()
    queue.submit(job)
    with pytest.raises(ValueError, match="job_not_leased"):
        queue.ack(job, _terminal_result(job))
    with pytest.raises(ValueError, match="job_not_leased"):
        queue.requeue(job)


def test_queue_bounds_redelivery_attempts() -> None:
    queue = InMemoryWorkQueue(QueueConfig(max_deliveries=2))
    job = _job()
    queue.submit(job)
    assert queue.lease() == job
    queue.requeue(job)
    assert queue.lease() == job
    assert queue.delivery_count(job) == 2
    with pytest.raises(ValueError, match="delivery_budget_exhausted"):
        queue.requeue(job)


def test_queue_rejects_mismatched_terminal_records() -> None:
    queue = InMemoryWorkQueue(QueueConfig())
    job = _job()
    queue.submit(job)
    assert queue.lease() == job
    wrong = _terminal_result(_job(job_id="job-wrong", key="key-wrong"))
    with pytest.raises(ValueError, match="result_job_mismatch"):
        queue.ack(job, wrong)


def test_dead_letter_transition_requires_matching_terminal_result() -> None:
    queue = InMemoryWorkQueue(QueueConfig())
    job = _job(scenario="invalid-api-result")
    queue.submit(job)
    assert queue.lease() == job
    record = DeadLetterRecord(
        job_id=job.job_id,
        tenant_id=job.tenant_id,
        scenario=job.scenario,
        code="invalid_response",
        delivery_count=1,
        dependency_attempt_count=1,
    )
    with pytest.raises(ValueError, match="dead_letter_record_mismatch"):
        queue.move_to_dead_letter(job, _terminal_result(job), record)


def test_job_contract_rejects_coercion_and_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Job.model_validate(
            {
                "job_id": 20,
                "tenant_id": "tenant-acme",
                "idempotency_key": "key",
                "scenario": "rate-limit-errors",
            }
        )
    with pytest.raises(ValidationError):
        Job.model_validate(
            {
                "job_id": "job",
                "tenant_id": "tenant-acme",
                "idempotency_key": "key",
                "scenario": "rate-limit-errors",
                "payload": "secret",
            }
        )


def test_batch_report_rejects_invented_counts() -> None:
    report = run_batch()
    with pytest.raises(ValidationError, match="batch_counts_disagree"):
        BatchReport(
            results=report.results,
            dead_letters=report.dead_letters,
            completed_count=99,
            degraded_count=report.degraded_count,
            dead_letter_count=report.dead_letter_count,
        )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_each_cli_case_emits_the_requested_scenario(scenario: Scenario) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.week_20.demo",
            "case",
            "--scenario",
            scenario,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = cast(dict[str, object], json.loads(completed.stdout))
    results = cast(list[dict[str, object]], payload["results"])
    assert results[0]["scenario"] == scenario


def test_cli_batch_and_smoke_commands() -> None:
    batch = subprocess.run(
        [sys.executable, "-m", "labs.week_20.demo", "batch"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(batch.stdout)["dead_letter_count"] == 1
    smoke = subprocess.run(
        [sys.executable, "-m", "labs.week_20.demo", "smoke"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(smoke.stdout) == {
        "checks": 16,
        "scenarios": 5,
        "status": "ok",
    }
