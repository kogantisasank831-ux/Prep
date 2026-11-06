"""Deterministic retries, circuits, fallbacks and queue handling for Week 20."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Final, cast

from pydantic import JsonValue

from labs.week_20.models import (
    AttemptOutcome,
    AttemptRecord,
    BatchReport,
    CallResolution,
    CircuitConfig,
    CircuitState,
    DeadLetterRecord,
    DependencyName,
    DependencyResponse,
    FailureKind,
    Job,
    JobResult,
    QueueConfig,
    ResultCode,
    RetryPolicy,
    Scenario,
)


TRANSIENT_OUTCOMES: Final[frozenset[AttemptOutcome]] = frozenset(
    {"unavailable", "rate_limited", "timeout"}
)


class ManualClock:
    """Advance virtual time without sleeping or reading the wall clock."""

    def __init__(self) -> None:
        self._now_ms = 0
        self._advances: list[int] = []

    @property
    def now_ms(self) -> int:
        return self._now_ms

    @property
    def advances(self) -> tuple[int, ...]:
        return tuple(self._advances)

    def advance(self, milliseconds: int) -> None:
        if milliseconds <= 0:
            raise ValueError("clock_advance_must_be_positive")
        self._now_ms += milliseconds
        self._advances.append(milliseconds)


class CircuitBreaker:
    """A sequential closed/open/half-open circuit for one dependency."""

    def __init__(self, config: CircuitConfig) -> None:
        self._config = config
        self._state: CircuitState = "closed"
        self._consecutive_failures = 0
        self._opened_at_ms: int | None = None

    @property
    def state(self) -> CircuitState:
        return self._state

    def allow_call(self, now_ms: int) -> bool:
        if self._state == "closed":
            return True
        if self._state == "open":
            assert self._opened_at_ms is not None
            if now_ms - self._opened_at_ms < self._config.recovery_timeout_ms:
                return False
            self._state = "half_open"
        return True

    def record_success(self) -> None:
        self._state = "closed"
        self._consecutive_failures = 0
        self._opened_at_ms = None

    def record_failure(self, now_ms: int) -> None:
        self._consecutive_failures += 1
        if (
            self._state == "half_open"
            or self._consecutive_failures >= self._config.failure_threshold
        ):
            self._state = "open"
            self._opened_at_ms = now_ms


class CircuitRegistry:
    """Keep failure state isolated by dependency name."""

    def __init__(self, config: CircuitConfig) -> None:
        self._config = config
        self._circuits: dict[DependencyName, CircuitBreaker] = {}

    def for_dependency(self, dependency: DependencyName) -> CircuitBreaker:
        circuit = self._circuits.get(dependency)
        if circuit is None:
            circuit = CircuitBreaker(self._config)
            self._circuits[dependency] = circuit
        return circuit


class ScriptedDependency:
    """Return a finite, inspectable response sequence without external I/O."""

    def __init__(
        self, dependency: DependencyName, responses: tuple[DependencyResponse, ...]
    ) -> None:
        if not responses:
            raise ValueError("script_requires_response")
        if any(response.dependency != dependency for response in responses):
            raise ValueError("script_dependency_mismatch")
        self.dependency = dependency
        self._responses = responses
        self._calls = 0

    @property
    def call_count(self) -> int:
        return self._calls

    def call(self) -> DependencyResponse:
        index = min(self._calls, len(self._responses) - 1)
        self._calls += 1
        return self._responses[index]


@dataclass(frozen=True, slots=True)
class DependencyTarget:
    adapter: ScriptedDependency
    required_fields: frozenset[str]


@dataclass(frozen=True, slots=True)
class ScenarioPlan:
    scenario: Scenario
    targets: tuple[DependencyTarget, ...]


def _response(
    dependency: DependencyName,
    status: str,
    *,
    elapsed_ms: int,
    data: dict[str, JsonValue] | None = None,
    retry_after_ms: int | None = None,
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


def build_scenario_plan(scenario: Scenario) -> ScenarioPlan:
    """Build fresh adapters so every run starts from the same fixture state."""

    if scenario == "llm-provider-outage":
        primary = ScriptedDependency(
            "model-primary",
            (
                _response("model-primary", "unavailable", elapsed_ms=20),
                _response("model-primary", "unavailable", elapsed_ms=25),
            ),
        )
        secondary = ScriptedDependency(
            "model-secondary",
            (
                _response(
                    "model-secondary",
                    "ok",
                    elapsed_ms=35,
                    data={"answer": "Manual review recommended", "model": "secondary"},
                ),
            ),
        )
        return ScenarioPlan(
            scenario,
            (
                DependencyTarget(primary, frozenset({"answer", "model"})),
                DependencyTarget(secondary, frozenset({"answer", "model"})),
            ),
        )
    if scenario == "database-timeout":
        database = ScriptedDependency(
            "database-primary",
            (
                _response(
                    "database-primary",
                    "ok",
                    elapsed_ms=250,
                    data={"orders": ["PO-918"]},
                ),
                _response(
                    "database-primary",
                    "ok",
                    elapsed_ms=220,
                    data={"orders": ["PO-918"]},
                ),
            ),
        )
        cache = ScriptedDependency(
            "bounded-cache",
            (
                _response(
                    "bounded-cache",
                    "ok",
                    elapsed_ms=2,
                    data={
                        "freshness": "stale-45s",
                        "orders": ["PO-918"],
                        "source": "bounded-cache",
                    },
                ),
            ),
        )
        return ScenarioPlan(
            scenario,
            (
                DependencyTarget(database, frozenset({"orders"})),
                DependencyTarget(cache, frozenset({"freshness", "orders", "source"})),
            ),
        )
    if scenario == "invalid-api-result":
        api = ScriptedDependency(
            "supplier-api",
            (
                _response(
                    "supplier-api",
                    "ok",
                    elapsed_ms=10,
                    data={"unexpected": True},
                ),
            ),
        )
        return ScenarioPlan(
            scenario, (DependencyTarget(api, frozenset({"supplier_id", "risk"})),)
        )
    if scenario == "vector-store-failure":
        vector = ScriptedDependency(
            "vector-store",
            (
                _response("vector-store", "unavailable", elapsed_ms=15),
                _response("vector-store", "unavailable", elapsed_ms=18),
            ),
        )
        lexical = ScriptedDependency(
            "lexical-search",
            (
                _response(
                    "lexical-search",
                    "ok",
                    elapsed_ms=8,
                    data={"documents": ["contract-171"], "retrieval": "lexical"},
                ),
            ),
        )
        return ScenarioPlan(
            scenario,
            (
                DependencyTarget(vector, frozenset({"documents"})),
                DependencyTarget(lexical, frozenset({"documents", "retrieval"})),
            ),
        )
    catalog = ScriptedDependency(
        "catalog-api",
        (
            _response(
                "catalog-api",
                "rate_limited",
                elapsed_ms=5,
                retry_after_ms=300,
            ),
            _response(
                "catalog-api",
                "ok",
                elapsed_ms=12,
                data={"items": ["SKU-20"], "source": "catalog-api"},
            ),
        ),
    )
    return ScenarioPlan(
        scenario, (DependencyTarget(catalog, frozenset({"items", "source"})),)
    )


def _classify(
    response: DependencyResponse, required_fields: frozenset[str], timeout_ms: int
) -> AttemptOutcome:
    if response.elapsed_ms > timeout_ms:
        return "timeout"
    if response.status == "ok":
        return "ok" if required_fields.issubset(response.data) else "invalid_response"
    if response.status == "unavailable":
        return "unavailable"
    if response.status == "rate_limited":
        return "rate_limited"
    if response.status == "invalid":
        return "invalid_response"
    return "dependency_failure"


class DependencyExecutor:
    """Apply one retry policy and per-dependency circuits to a declared chain."""

    def __init__(
        self,
        *,
        clock: ManualClock,
        retry_policy: RetryPolicy,
        circuits: CircuitRegistry,
    ) -> None:
        self._clock = clock
        self._retry_policy = retry_policy
        self._circuits = circuits

    def _backoff(self, attempt: int, response: DependencyResponse) -> int:
        exponential = cast(
            int,
            min(
                self._retry_policy.max_backoff_ms,
                self._retry_policy.base_backoff_ms * (2 ** (attempt - 1)),
            ),
        )
        if response.retry_after_ms is None:
            return exponential
        retry_after = min(
            response.retry_after_ms, self._retry_policy.max_retry_after_ms
        )
        return max(exponential, retry_after)

    def execute(self, plan: ScenarioPlan) -> CallResolution:
        attempts: list[AttemptRecord] = []
        last_outcome: AttemptOutcome = "dependency_failure"
        last_failure_kind: FailureKind = "permanent"

        for target_index, target in enumerate(plan.targets):
            dependency = target.adapter.dependency
            circuit = self._circuits.for_dependency(dependency)
            for attempt in range(1, self._retry_policy.max_attempts + 1):
                if not circuit.allow_call(self._clock.now_ms):
                    last_outcome = "circuit_open"
                    last_failure_kind = "transient"
                    attempts.append(
                        AttemptRecord(
                            dependency=dependency,
                            attempt=attempt,
                            invoked=False,
                            outcome="circuit_open",
                            elapsed_ms=0,
                            scheduled_backoff_ms=0,
                            circuit_state_after=circuit.state,
                        )
                    )
                    break

                response = target.adapter.call()
                outcome = _classify(
                    response, target.required_fields, self._retry_policy.timeout_ms
                )
                last_outcome = outcome
                if outcome == "ok":
                    circuit.record_success()
                    attempts.append(
                        AttemptRecord(
                            dependency=dependency,
                            attempt=attempt,
                            invoked=True,
                            outcome=outcome,
                            elapsed_ms=response.elapsed_ms,
                            scheduled_backoff_ms=0,
                            circuit_state_after=circuit.state,
                        )
                    )
                    if target_index > 0:
                        return CallResolution(
                            status="degraded",
                            code="fallback_used",
                            failure_kind="none",
                            selected_dependency=dependency,
                            data=response.data,
                            warnings=(
                                "primary_dependency_failed",
                                f"degraded_fallback:{dependency}",
                            ),
                            attempts=tuple(attempts),
                        )
                    code: ResultCode = "recovered_after_retry" if attempt > 1 else "ok"
                    warnings = ("retry_recovered",) if attempt > 1 else ()
                    return CallResolution(
                        status="completed",
                        code=code,
                        failure_kind="none",
                        selected_dependency=dependency,
                        data=response.data,
                        warnings=warnings,
                        attempts=tuple(attempts),
                    )

                circuit.record_failure(self._clock.now_ms)
                last_failure_kind = (
                    "transient" if outcome in TRANSIENT_OUTCOMES else "permanent"
                )
                should_retry = (
                    last_failure_kind == "transient"
                    and attempt < self._retry_policy.max_attempts
                    and circuit.state != "open"
                )
                delay = self._backoff(attempt, response) if should_retry else 0
                attempts.append(
                    AttemptRecord(
                        dependency=dependency,
                        attempt=attempt,
                        invoked=True,
                        outcome=outcome,
                        elapsed_ms=response.elapsed_ms,
                        scheduled_backoff_ms=delay,
                        circuit_state_after=circuit.state,
                    )
                )
                if delay:
                    self._clock.advance(delay)
                    continue
                break

        code = self._failure_code(last_outcome, last_failure_kind)
        return CallResolution(
            status="failed",
            code=code,
            failure_kind=last_failure_kind,
            selected_dependency=None,
            data={},
            warnings=("no_usable_dependency",),
            attempts=tuple(attempts),
        )

    @staticmethod
    def _failure_code(outcome: AttemptOutcome, failure_kind: FailureKind) -> ResultCode:
        if failure_kind == "transient" and outcome not in {"circuit_open"}:
            return "retry_exhausted"
        mapping: dict[AttemptOutcome, ResultCode] = {
            "ok": "ok",
            "unavailable": "dependency_unavailable",
            "rate_limited": "rate_limited",
            "timeout": "timeout",
            "invalid_response": "invalid_response",
            "dependency_failure": "dependency_failure",
            "circuit_open": "circuit_open",
        }
        return mapping[outcome]


class InMemoryWorkQueue:
    """A deterministic at-least-once teaching queue with idempotent submission."""

    def __init__(self, config: QueueConfig) -> None:
        self.config = config
        self._pending: deque[Job] = deque()
        self._in_flight: dict[str, Job] = {}
        self._deliveries: dict[str, int] = {}
        self._job_ids: set[str] = set()
        self._fingerprints: dict[str, tuple[str, Scenario]] = {}
        self._results: dict[str, JobResult] = {}
        self._result_order: list[str] = []
        self._dead_letters: list[DeadLetterRecord] = []

    @property
    def results(self) -> tuple[JobResult, ...]:
        return tuple(self._results[key] for key in self._result_order)

    @property
    def dead_letters(self) -> tuple[DeadLetterRecord, ...]:
        return tuple(self._dead_letters)

    def submit(self, job: Job) -> bool:
        fingerprint = (job.tenant_id, job.scenario)
        known = self._fingerprints.get(job.idempotency_key)
        if known is not None:
            if known != fingerprint:
                raise ValueError("idempotency_key_conflict")
            return False
        if job.job_id in self._job_ids:
            raise ValueError("duplicate_job_id")
        self._fingerprints[job.idempotency_key] = fingerprint
        self._job_ids.add(job.job_id)
        self._pending.append(job)
        return True

    def lease(self) -> Job | None:
        if not self._pending:
            return None
        job = self._pending.popleft()
        self._deliveries[job.job_id] = self._deliveries.get(job.job_id, 0) + 1
        self._in_flight[job.job_id] = job
        return job

    def delivery_count(self, job: Job) -> int:
        return self._deliveries[job.job_id]

    def ack(self, job: Job, result: JobResult) -> None:
        self._require_lease(job)
        if result.job_id != job.job_id:
            raise ValueError("result_job_mismatch")
        del self._in_flight[job.job_id]
        self._results[job.idempotency_key] = result
        self._result_order.append(job.idempotency_key)

    def requeue(self, job: Job) -> None:
        self._require_lease(job)
        if self.delivery_count(job) >= self.config.max_deliveries:
            raise ValueError("delivery_budget_exhausted")
        del self._in_flight[job.job_id]
        self._pending.append(job)

    def move_to_dead_letter(
        self, job: Job, result: JobResult, record: DeadLetterRecord
    ) -> None:
        self._require_lease(job)
        if result.status != "dead_letter" or record.job_id != job.job_id:
            raise ValueError("dead_letter_record_mismatch")
        del self._in_flight[job.job_id]
        self._results[job.idempotency_key] = result
        self._result_order.append(job.idempotency_key)
        self._dead_letters.append(record)

    def result_for(self, idempotency_key: str) -> JobResult | None:
        return self._results.get(idempotency_key)

    def _require_lease(self, job: Job) -> None:
        if self._in_flight.get(job.job_id) != job:
            raise ValueError("job_not_leased")


class ReliableWorker:
    """Process independent jobs, preserving partial success and terminal evidence."""

    def __init__(
        self,
        *,
        retry_policy: RetryPolicy | None = None,
        circuit_config: CircuitConfig | None = None,
        queue_config: QueueConfig | None = None,
    ) -> None:
        self.clock = ManualClock()
        self.circuits = CircuitRegistry(circuit_config or CircuitConfig())
        self.executor = DependencyExecutor(
            clock=self.clock,
            retry_policy=retry_policy or RetryPolicy(),
            circuits=self.circuits,
        )
        self.queue = InMemoryWorkQueue(queue_config or QueueConfig())

    def run(self, jobs: tuple[Job, ...]) -> BatchReport:
        for job in jobs:
            self.queue.submit(job)

        while True:
            leased_job = self.queue.lease()
            if leased_job is None:
                break
            job = leased_job
            resolution = self.executor.execute(build_scenario_plan(job.scenario))
            delivery_count = self.queue.delivery_count(job)
            if resolution.status != "failed":
                result = JobResult(
                    job_id=job.job_id,
                    scenario=job.scenario,
                    status=resolution.status,
                    code=resolution.code,
                    selected_dependency=resolution.selected_dependency,
                    data=resolution.data,
                    warnings=resolution.warnings,
                    attempts=resolution.attempts,
                    delivery_count=delivery_count,
                )
                self.queue.ack(job, result)
                continue

            if (
                resolution.failure_kind == "transient"
                and delivery_count < self.queue.config.max_deliveries
            ):
                self.queue.requeue(job)
                continue

            result = JobResult(
                job_id=job.job_id,
                scenario=job.scenario,
                status="dead_letter",
                code=resolution.code,
                selected_dependency=None,
                data={},
                warnings=resolution.warnings,
                attempts=resolution.attempts,
                delivery_count=delivery_count,
            )
            record = DeadLetterRecord(
                job_id=job.job_id,
                tenant_id=job.tenant_id,
                scenario=job.scenario,
                code=resolution.code,
                delivery_count=delivery_count,
                dependency_attempt_count=len(resolution.attempts),
            )
            self.queue.move_to_dead_letter(job, result, record)

        results = self.queue.results
        return BatchReport(
            results=results,
            dead_letters=self.queue.dead_letters,
            completed_count=sum(result.status == "completed" for result in results),
            degraded_count=sum(result.status == "degraded" for result in results),
            dead_letter_count=sum(result.status == "dead_letter" for result in results),
        )
