"""Bounded supervisor and sequential baseline over the same specialists."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, cast

from labs.week_17.models import (
    Architecture,
    ArchitectureComparison,
    Assignment,
    CommercialAssignment,
    CommercialFinding,
    CoordinationMetrics,
    DocumentAssignment,
    DocumentFinding,
    FirstWaveFinding,
    ProcurementCase,
    RiskAssignment,
    RiskFinding,
    RunResult,
    RunStatus,
    SpecialistName,
    SpecialistResult,
    SqlAssignment,
    SqlFinding,
)
from labs.week_17.specialists import (
    DEFAULT_SPECIALISTS,
    SpecialistFailure,
    SpecialistFunction,
)


FIRST_WAVE: tuple[SpecialistName, ...] = (
    SpecialistName.DOCUMENT,
    SpecialistName.SQL,
    SpecialistName.SUPPLIER_RISK,
)
EXPECTED_RESULT_TYPES: dict[SpecialistName, type[SpecialistResult]] = {
    SpecialistName.DOCUMENT: DocumentFinding,
    SpecialistName.SQL: SqlFinding,
    SpecialistName.SUPPLIER_RISK: RiskFinding,
    SpecialistName.COMMERCIAL: CommercialFinding,
}


def _assignments(
    case: ProcurementCase, run_id: str
) -> dict[SpecialistName, Assignment]:
    return {
        SpecialistName.DOCUMENT: DocumentAssignment(
            run_id=run_id,
            case_id=case.case_id,
            purchase_order_id=case.purchase_order_id,
            source=case.document_source,
        ),
        SpecialistName.SQL: SqlAssignment(
            run_id=run_id,
            case_id=case.case_id,
            purchase_order_id=case.purchase_order_id,
            selected_supplier_id=case.selected_supplier_id,
            source=case.sql_source,
        ),
        SpecialistName.SUPPLIER_RISK: RiskAssignment(
            run_id=run_id,
            case_id=case.case_id,
            selected_supplier_id=case.selected_supplier_id,
            source=case.risk_source,
        ),
    }


def _validate_result(
    result: SpecialistResult,
    expected: SpecialistName,
    *,
    run_id: str,
    case_id: str,
) -> None:
    if not isinstance(result, EXPECTED_RESULT_TYPES[expected]):
        raise ValueError("result_type_mismatch")
    if result.specialist is not expected:
        raise ValueError("result_specialist_mismatch")
    if result.run_id != run_id:
        raise ValueError("result_run_mismatch")
    if result.case_id != case_id:
        raise ValueError("result_case_mismatch")


def _error_code(error: Exception) -> str:
    """Expose controlled domain codes without leaking unexpected exception text."""
    if isinstance(error, (SpecialistFailure, ValueError)):
        return str(error)
    return f"unexpected_{type(error).__name__}"


def _failed(
    architecture: Architecture,
    run_id: str,
    case_id: str,
    trace: list[str],
    findings: list[FirstWaveFinding],
    reason: str,
    calls: int,
    *,
    max_workers: int,
) -> RunResult:
    trace.append(f"{architecture}:failed:{reason}")
    return RunResult(
        architecture=architecture,
        run_id=run_id,
        case_id=case_id,
        status=RunStatus.FAILED,
        report=None,
        findings=tuple(findings),
        metrics=CoordinationMetrics(
            specialist_calls=calls,
            handoffs=calls if architecture is Architecture.SUPERVISOR else 0,
            parallel_groups=(
                1 if architecture is Architecture.SUPERVISOR and calls > 0 else 0
            ),
            dependency_stages=(
                min(2, calls) if architecture is Architecture.SUPERVISOR else calls
            ),
            max_parallel_workers=max_workers,
        ),
        trace=tuple(trace),
        failure_reason=reason,
    )


@dataclass(frozen=True)
class Supervisor:
    """Own routing and aggregation while specialists remain stateless."""

    specialists: Mapping[SpecialistName, SpecialistFunction]
    max_workers: int = 3

    def __post_init__(self) -> None:
        if not 1 <= self.max_workers <= len(FIRST_WAVE):
            raise ValueError("max_workers_out_of_range")
        object.__setattr__(
            self,
            "specialists",
            MappingProxyType(dict(self.specialists)),
        )

    def run(self, case: ProcurementCase, *, run_id: str) -> RunResult:
        trace = ["supervisor:start"]
        findings: list[FirstWaveFinding] = []
        missing = [name for name in SpecialistName if name not in self.specialists]
        if missing:
            reason = f"registry_incomplete:{missing[0]}"
            return _failed(
                Architecture.SUPERVISOR,
                run_id,
                case.case_id,
                trace,
                findings,
                reason,
                0,
                max_workers=self.max_workers,
            )

        assignments = _assignments(case, run_id)
        futures: dict[SpecialistName, Future[SpecialistResult]] = {}
        with ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="week17-specialist",
        ) as executor:
            for name in FIRST_WAVE:
                trace.append(f"supervisor:dispatch:{name}")
                futures[name] = executor.submit(
                    self.specialists[name], assignments[name]
                )

            for name in FIRST_WAVE:
                try:
                    result = futures[name].result()
                    _validate_result(
                        result,
                        name,
                        run_id=run_id,
                        case_id=case.case_id,
                    )
                except Exception as error:
                    for future in futures.values():
                        future.cancel()
                    reason = f"specialist_failed:{name}:{_error_code(error)}"
                    return _failed(
                        Architecture.SUPERVISOR,
                        run_id,
                        case.case_id,
                        trace,
                        findings,
                        reason,
                        len(futures),
                        max_workers=self.max_workers,
                    )
                finding = cast(FirstWaveFinding, result)
                findings.append(finding)
                trace.append(f"supervisor:complete:{name}")

        document = cast(DocumentFinding, findings[0])
        sql = cast(SqlFinding, findings[1])
        risk = cast(RiskFinding, findings[2])
        commercial_assignment = CommercialAssignment(
            run_id=run_id,
            case_id=case.case_id,
            document=document,
            sql=sql,
            risk=risk,
        )
        trace.append("supervisor:dispatch:commercial")
        try:
            commercial = self.specialists[SpecialistName.COMMERCIAL](
                commercial_assignment
            )
            _validate_result(
                commercial,
                SpecialistName.COMMERCIAL,
                run_id=run_id,
                case_id=case.case_id,
            )
        except Exception as error:
            return _failed(
                Architecture.SUPERVISOR,
                run_id,
                case.case_id,
                trace,
                findings,
                f"specialist_failed:commercial:{_error_code(error)}",
                4,
                max_workers=self.max_workers,
            )
        report = cast(CommercialFinding, commercial)
        trace.extend(("supervisor:complete:commercial", "supervisor:awaiting_approval"))
        return RunResult(
            architecture=Architecture.SUPERVISOR,
            run_id=run_id,
            case_id=case.case_id,
            status=RunStatus.AWAITING_APPROVAL,
            report=report,
            findings=tuple(findings),
            metrics=CoordinationMetrics(
                specialist_calls=4,
                handoffs=4,
                parallel_groups=1,
                dependency_stages=2,
                max_parallel_workers=self.max_workers,
            ),
            trace=tuple(trace),
        )


def default_supervisor() -> Supervisor:
    """Return a fresh registry wrapper for the built-in specialists."""
    return Supervisor(dict(DEFAULT_SPECIALISTS))


def run_single_workflow(
    case: ProcurementCase,
    *,
    run_id: str,
    specialists: Mapping[SpecialistName, SpecialistFunction] | None = None,
) -> RunResult:
    """Run the same components sequentially without inter-agent coordination."""
    registry = dict(DEFAULT_SPECIALISTS if specialists is None else specialists)
    trace = ["single_workflow:start"]
    findings: list[FirstWaveFinding] = []
    missing = [name for name in SpecialistName if name not in registry]
    if missing:
        return _failed(
            Architecture.SINGLE_WORKFLOW,
            run_id,
            case.case_id,
            trace,
            findings,
            f"registry_incomplete:{missing[0]}",
            0,
            max_workers=1,
        )
    assignments = _assignments(case, run_id)
    calls = 0
    for name in FIRST_WAVE:
        calls += 1
        try:
            result = registry[name](assignments[name])
            _validate_result(
                result,
                name,
                run_id=run_id,
                case_id=case.case_id,
            )
        except Exception as error:
            return _failed(
                Architecture.SINGLE_WORKFLOW,
                run_id,
                case.case_id,
                trace,
                findings,
                f"component_failed:{name}:{_error_code(error)}",
                calls,
                max_workers=1,
            )
        findings.append(cast(FirstWaveFinding, result))
        trace.append(f"single_workflow:complete:{name}")

    calls += 1
    assignment = CommercialAssignment(
        run_id=run_id,
        case_id=case.case_id,
        document=cast(DocumentFinding, findings[0]),
        sql=cast(SqlFinding, findings[1]),
        risk=cast(RiskFinding, findings[2]),
    )
    try:
        commercial = registry[SpecialistName.COMMERCIAL](assignment)
        _validate_result(
            commercial,
            SpecialistName.COMMERCIAL,
            run_id=run_id,
            case_id=case.case_id,
        )
    except Exception as error:
        return _failed(
            Architecture.SINGLE_WORKFLOW,
            run_id,
            case.case_id,
            trace,
            findings,
            f"component_failed:commercial:{_error_code(error)}",
            calls,
            max_workers=1,
        )
    trace.extend(
        ("single_workflow:complete:commercial", "single_workflow:awaiting_approval")
    )
    return RunResult(
        architecture=Architecture.SINGLE_WORKFLOW,
        run_id=run_id,
        case_id=case.case_id,
        status=RunStatus.AWAITING_APPROVAL,
        report=cast(CommercialFinding, commercial),
        findings=tuple(findings),
        metrics=CoordinationMetrics(
            specialist_calls=4,
            handoffs=0,
            parallel_groups=0,
            dependency_stages=4,
            max_parallel_workers=1,
        ),
        trace=tuple(trace),
    )


def compare_architectures(
    case: ProcurementCase,
    *,
    run_id: str,
) -> ArchitectureComparison:
    """Compare observable outcomes and structural coordination costs."""
    supervisor = default_supervisor().run(case, run_id=run_id)
    workflow = run_single_workflow(case, run_id=run_id)
    supervisor_recommendation = (
        supervisor.report.recommendation if supervisor.report else None
    )
    workflow_recommendation = (
        workflow.report.recommendation if workflow.report else None
    )
    outcome_equal = (
        supervisor.status is workflow.status
        and supervisor.report == workflow.report
        and supervisor.failure_reason == workflow.failure_reason
    )
    return ArchitectureComparison(
        case_id=case.case_id,
        outcome_equal=outcome_equal,
        supervisor_recommendation=supervisor_recommendation,
        workflow_recommendation=workflow_recommendation,
        supervisor_handoffs=supervisor.metrics.handoffs,
        workflow_handoffs=workflow.metrics.handoffs,
        supervisor_dependency_stages=supervisor.metrics.dependency_stages,
        workflow_dependency_stages=workflow.metrics.dependency_stages,
        conclusion=(
            "The supervisor exposes isolated ownership and one parallel wave, but "
            "adds four validated handoffs. Prefer the single workflow when these "
            "boundaries do not justify that coordination cost."
        ),
    )
