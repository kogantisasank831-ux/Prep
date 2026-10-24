"""Observable behavior, provenance, timing and application/telemetry boundaries."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
from typing import cast

import pytest

from labs.week_07.retrieval import RetrievalRequest
from labs.week_08.data import demo_access, load_corpus
from labs.week_08.pipeline import KnowledgeAssistant, PipelineError, TeachingPairScorer
from labs.week_09.dataset import EvaluationCase, load_cases
from labs.week_09.run import DATASET_DIR
from labs.week_10.demo import (
    CORPUS,
    FixtureModel,
    illustrative_prices,
    save_trace,
    scenario_case,
    synthetic_content,
)
from labs.week_10.generation import (
    Completion,
    ModelIdentity,
    Prompt,
    RateCard,
    Usage,
    build_prompt,
    estimate_cost,
)
from labs.week_10.pipeline import ObservedResult, observe_request
from labs.week_10.tracing import (
    ModelOutputError,
    Span,
    Stage,
    TraceError,
    TraceRecorder,
    deliver,
)


class Clock:
    def __init__(self) -> None:
        self.tick = -1_000_000

    def __call__(self) -> int:
        self.tick += 1_000_000
        return self.tick


class IDs:
    def __init__(self) -> None:
        self.number = 0

    def __call__(self, size: int) -> str:
        self.number += 1
        return f"{self.number:0{size * 2}x}"


def recorder(**kwargs: object) -> TraceRecorder:
    factory = cast(Callable[..., TraceRecorder], TraceRecorder)
    return factory(
        "test-request",
        clock=Clock(),
        ids=IDs(),
        utc_now=lambda: datetime(2026, 10, 24, tzinfo=timezone.utc),
        clock_source="scripted_test",
        **kwargs,
    )


def run(name: str = "payment") -> tuple[ObservedResult, TraceRecorder]:
    case = scenario_case(name)
    trace = recorder()
    result = observe_request(
        case.request,
        load_corpus(CORPUS).chunks,
        demo_access(),
        trace,
        config=case.config,
        rewrites=case.rewrites,
        model=case.model,
        prices=illustrative_prices() if case.model else None,
    )
    return result, trace


def test_parent_ids_and_inclusive_monotonic_intervals() -> None:
    trace = recorder()
    with trace.span(Stage.REQUEST) as root:
        with trace.span(Stage.RETRIEVAL, parent=root):
            pass
    child, parent = trace.records
    assert len(trace.trace_id) == 32 and len(parent.span_id) == 16
    assert child.parent_span_id == parent.span_id
    assert parent.parent_span_id is None
    assert parent.start_offset_ns == 1_000_000
    assert parent.duration_ns == 3_000_000 and child.duration_ns == 1_000_000
    assert trace.document()["telemetry_complete"] is True


def test_request_ownership_and_lifecycle_are_enforced() -> None:
    trace, foreign = recorder(), recorder()
    with pytest.raises(TraceError):
        trace.document()
    with trace.span(Stage.REQUEST) as root:
        with pytest.raises(TraceError):
            trace.document()
        with pytest.raises(TraceError):
            with foreign.span(Stage.TOOL, parent=root):
                pass
        forged = Span(trace, Stage.RETRIEVAL, root, "0000000000000099", 0)
        with pytest.raises(TraceError):
            with trace.span(Stage.TOOL, parent=forged):
                pass
    with pytest.raises(TraceError):
        root.set(outcome="late")
    with pytest.raises(TraceError):
        with trace.span(Stage.TOOL, parent=root):
            pass
    with pytest.raises(TraceError):
        with trace.span(Stage.REQUEST):
            pass


@pytest.mark.parametrize("value", ["", "0" * 32, "a" * 31, "A" * 32, "not-an-id"])
def test_invalid_identity_factory_is_a_setup_failure(value: str) -> None:
    with pytest.raises(TraceError):
        TraceRecorder("test", ids=lambda size: value)


@pytest.mark.parametrize("capacity", [0, -1, 257, True])
def test_span_budget_is_bounded(capacity: int) -> None:
    with pytest.raises(TraceError):
        recorder(max_spans=capacity)


def test_span_overflow_is_visible_and_does_not_skip_application_work() -> None:
    trace = recorder(max_spans=2)
    work = []
    with trace.span(Stage.REQUEST) as root:
        with trace.span(Stage.RETRIEVAL, parent=root) as parent:
            with trace.span(Stage.TOOL, parent=parent) as dropped:
                work.append(1)
                with trace.span(Stage.CONTEXT, parent=dropped):
                    work.append(2)
    assert work == [1, 2] and len(trace.records) == 2
    assert trace.document()["dropped_span_count"] == 2
    assert trace.document()["telemetry_complete"] is False
    ids = {span.span_id for span in trace.records}
    assert all(
        s.parent_span_id is None or s.parent_span_id in ids for s in trace.records
    )


@pytest.mark.parametrize(
    "attributes",
    [
        {"query": "secret"},
        {"prompt": "secret"},
        {"exception_message": "secret"},
        {"candidate_ids": tuple("id" for _ in range(33))},
        {"model_id": "x" * 257},
        {"retrieval_scores": (float("nan"),)},
        {"retrieval_scores": (float("inf"),)},
        {"input_tokens": 10**16},
        {"candidate_ids": ["mutable"]},
    ],
)
def test_metadata_projection_rejects_unbounded_or_payload_fields(
    attributes: dict[str, object],
) -> None:
    trace = recorder()
    with trace.span(Stage.REQUEST) as root:
        with pytest.raises(TraceError):
            cast(Callable[..., None], root.set)(**attributes)


@pytest.mark.parametrize("reading", [True, -1, 1.2, "3", None])
def test_invalid_clock_never_invents_zero_duration(reading: object) -> None:
    trace = TraceRecorder("clock", clock=cast(Callable[[], int], lambda: reading))
    with trace.span(Stage.REQUEST):
        pass
    assert trace.records[0].duration_ns is None
    assert trace.document()["timing_error_count"] == 3
    assert trace.document()["telemetry_complete"] is False


def test_backwards_and_raising_clocks_leave_missing_intervals() -> None:
    readings = iter([10, 9, 12])
    trace = TraceRecorder("clock", clock=lambda: next(readings))
    with trace.span(Stage.REQUEST):
        pass
    assert trace.records[0].duration_ns is None
    assert trace.timing_errors == 1
    trace = TraceRecorder("clock", clock=lambda: next(iter([])))
    with trace.span(Stage.REQUEST):
        pass
    assert trace.timing_errors == 3


@pytest.mark.parametrize(
    "error,code,status",
    [
        (TimeoutError("SECRET credentials"), "timeout", "error"),
        (PermissionError("SECRET credentials"), "permission", "error"),
        (ValueError("SECRET credentials"), "validation", "error"),
        (RuntimeError("SECRET credentials"), "internal", "error"),
        (KeyboardInterrupt("SECRET credentials"), "cancelled", "cancelled"),
        (asyncio.CancelledError("SECRET credentials"), "cancelled", "cancelled"),
    ],
)
def test_original_failure_is_reraised_and_payload_stays_out(
    error: BaseException, code: str, status: str
) -> None:
    trace = recorder()
    with pytest.raises(type(error)) as raised:
        with trace.span(Stage.REQUEST) as root:
            with trace.span(Stage.MODEL, parent=root):
                raise error
    assert raised.value is error
    assert all(s.error_code == code and s.status == status for s in trace.records)
    assert "SECRET" not in json.dumps(trace.document())


def test_sink_failure_has_one_attempt_and_preserves_the_observed_answer() -> None:
    result, trace = run()
    calls = []

    def broken(document: dict[str, object]) -> None:
        calls.append(document)
        raise OSError("unavailable path")

    delivery = deliver(trace, broken)
    assert not delivery.delivered and delivery.error_code == "telemetry_delivery_failed"
    assert len(calls) == 1
    assert "Net 30 after inspection approval" in result.answer


@pytest.mark.parametrize(
    "counts",
    [(True, 1, 0), (-1, 1, 0), (1, 1, 2), (None, 1, 0), (100_000_001, 1, 0)],
)
def test_token_counts_are_exact_and_cached_is_a_subset(
    counts: tuple[int | None, int, int],
) -> None:
    with pytest.raises(ModelOutputError):
        Usage(*counts, "provider_reported")


@pytest.mark.parametrize("source", ["not_reported", "not_applicable"])
def test_unknown_usage_cannot_claim_counts(source: str) -> None:
    factory = cast(Callable[..., Usage], Usage)
    with pytest.raises(ModelOutputError):
        factory(0, 0, 0, source)


@pytest.mark.parametrize(
    "rate",
    [
        None,
        2.0,
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-1"),
        Decimal("0.0000000001"),
    ],
)
def test_invalid_rates_do_not_enter_cost_arithmetic(rate: object) -> None:
    factory = cast(Callable[..., RateCard], RateCard)
    with pytest.raises(ValueError):
        factory("test/v1", "USD", rate, Decimal("8"))


def test_cost_uses_exact_per_million_rates_without_double_counting_cache() -> None:
    prices = illustrative_prices()
    assert estimate_cost(
        Usage(1000, 300, 0, "synthetic_fixture"), prices
    ).amount == Decimal("0.0044")
    cached = estimate_cost(Usage(1000, 300, 200, "provider_reported"), prices)
    assert cached.amount == Decimal("0.0041")
    assert (
        cached.reason == "reported_usage_estimate"
        and cached.price_id == prices.identity
    )
    assert estimate_cost(Usage(0, 0, 0, "provider_reported"), prices).amount == 0
    assert estimate_cost(Usage(None, None, None, "not_reported"), prices).amount is None
    assert (
        estimate_cost(Usage(1000, 300, None, "provider_reported"), prices).reason
        == "cache_usage_unknown"
    )
    assert (
        estimate_cost(
            Usage(1000, 300, 1, "provider_reported"),
            replace(prices, cached_input_per_million=None),
        ).reason
        == "cache_price_unknown"
    )
    assert estimate_cost(Usage(1, 1, 0, "estimated"), prices).amount is None
    assert (
        estimate_cost(Usage(1, 1, 0, "provider_reported"), None).reason
        == "price_unavailable"
    )


def test_prompt_is_explicit_raw_text_and_malformed_output_is_rejected() -> None:
    prompt = build_prompt("When?", '[{"quote":"Net 30","citation_id":"S1"}]')
    assert prompt.messages[0][0] == "system" and prompt.messages[1][0] == "user"
    assert json.loads(prompt.messages[1][1])["evidence"][0]["quote"] == "Net 30"
    for text in ("", " ", "x" * 8001, "\ud800"):
        with pytest.raises(ModelOutputError):
            Completion(text, Usage(None, None, None, "not_reported"))
    with pytest.raises(ModelOutputError):
        Prompt("v1", (("assistant", "text"), ("user", "text")))
    with pytest.raises(ModelOutputError):
        Prompt("v1", (("system", "x" * 20000), ("user", "text")))


@pytest.mark.parametrize(
    "case", load_cases(DATASET_DIR / "cases.jsonl"), ids=lambda case: case.query_id
)
def test_tracing_preserves_all_30_week9_extractive_results(
    case: EvaluationCase,
) -> None:
    chunks = load_corpus(CORPUS).chunks
    request = case.request(top_k=3)
    expected = KnowledgeAssistant(chunks, demo_access()).ask(request)
    trace = recorder()
    actual = observe_request(request, chunks, demo_access(), trace)
    assert actual.retrieval == expected
    assert actual.answer == expected.answer
    root = trace.records[-1]
    assert root.status == "ok"
    assert dict(root.attributes)["usage_source"] == "not_applicable"
    assert dict(root.attributes)["input_tokens"] is None
    assert not any(s.name == "model" for s in trace.records)


def test_denied_sources_do_not_change_results_or_metadata() -> None:
    chunks = load_corpus(CORPUS).chunks
    request = scenario_case("payment").request
    left, right = recorder(), recorder()
    first = observe_request(request, chunks, demo_access(), left)
    public = tuple(c for c in chunks if c.document_id != "PRIVATE")
    second = observe_request(request, public, demo_access(), right)
    assert first == second
    assert [s.attributes for s in left.records] == [s.attributes for s in right.records]
    text = json.dumps(left.document())
    assert (
        request.query_text not in text
        and "Net 30" not in text
        and "SECRET-900" not in text
    )
    denied, trace = run("denied")
    assert denied.retrieval.status == "no_evidence" and not denied.retrieval.candidates
    assert trace.records[-1].status == "ok"


class InspectScorer:
    identity = TeachingPairScorer().identity

    def __init__(self) -> None:
        self.queries: list[str] = []

    def score_pairs(self, pairs: Sequence[tuple[str, str]]) -> tuple[float, ...]:
        self.queries.extend(q for q, _ in pairs)
        return tuple(0.0 for _ in pairs)


def test_rewrites_have_distinct_tool_spans_but_rerank_uses_original_question() -> None:
    trace, scorer = recorder(), InspectScorer()
    observe_request(
        RetrievalRequest("analyst", "CW-1000", 3),
        load_corpus(CORPUS).chunks,
        demo_access(),
        trace,
        rewrites=("CW-1000 catalogue",),
        scorer=scorer,
    )
    tools = [s for s in trace.records if s.name == Stage.TOOL]
    assert [dict(s.attributes)["query_index"] for s in tools] == [0, 1]
    assert len({s.parent_span_id for s in tools}) == 1
    assert scorer.queries and set(scorer.queries) == {"CW-1000"}
    trace = recorder()
    case = scenario_case("bad-rewrite")
    with pytest.raises(PipelineError):
        observe_request(
            case.request,
            load_corpus(CORPUS).chunks,
            demo_access(),
            trace,
            rewrites=case.rewrites,
        )
    assert trace.records[-1].error_code == "validation"


def test_paired_budget_change_localizes_loss_to_context() -> None:
    full, full_trace = run()
    tight, tight_trace = run("tight")
    assert full.retrieval.candidates == tight.retrieval.candidates
    assert full.retrieval.reranked == tight.retrieval.reranked
    assert "Net 30 after inspection approval" in full.answer
    assert "Net 30 after inspection approval" in tight.answer
    assert "controls Schedule A" in full.answer
    assert "controls Schedule A" not in tight.answer
    assert "1,000 kg" in full.answer and "1,000 kg" not in tight.answer
    assert (
        dict(full_trace.records[-1].attributes)["config_id"]
        != dict(tight_trace.records[-1].attributes)["config_id"]
    )
    for trace in (full_trace, tight_trace):
        context = next(s for s in trace.records if s.name == Stage.CONTEXT)
        selected = dict(context.attributes)["selected_ids"]
        assert isinstance(selected, tuple) and len(selected) == len(set(selected))


def test_fixture_model_is_observed_separately_and_usage_is_labelled_synthetic() -> None:
    result, trace = run("model-fixture")
    assert result.model is not None
    assert result.answer == result.retrieval.answer
    assert result.answer != result.model.completion.text
    model = next(s for s in trace.records if s.name == Stage.MODEL)
    attrs = dict(model.attributes)
    assert attrs["usage_source"] == "synthetic_fixture"
    assert attrs["cost_estimate"] == "0.0044"
    capture = json.dumps(synthetic_content(scenario_case("model-fixture"), result))
    assert "Net 30" in capture and "SECRET-900" not in capture
    assert "Net 30" not in json.dumps(trace.document())


@pytest.mark.parametrize(
    "scenario,code", [("model-timeout", "timeout"), ("model-invalid", "model_contract")]
)
def test_model_failures_leave_missing_usage_and_propagate(
    scenario: str, code: str
) -> None:
    case, trace = scenario_case(scenario), recorder()
    with pytest.raises((TimeoutError, ModelOutputError)):
        observe_request(
            case.request,
            load_corpus(CORPUS).chunks,
            demo_access(),
            trace,
            model=case.model,
        )
    model = next(s for s in trace.records if s.name == Stage.MODEL)
    assert model.error_code == code and trace.records[-1].error_code == code
    assert dict(model.attributes)["input_tokens"] is None
    assert "synthetic provider details" not in json.dumps(trace.document())


class DriftingModel:
    identity = ModelIdentity("fake", "v1", "provider")

    def __init__(self, drift: bool) -> None:
        self.drift = drift
        self.calls = 0

    def generate(self, prompt: Prompt) -> Completion:
        self.calls += 1
        if self.drift:
            self.identity = replace(self.identity, revision="v2")
        return FixtureModel().generate(prompt)


@pytest.mark.parametrize("drift", [True, False])
def test_identity_drift_and_fixture_provider_provenance_mix_are_rejected(
    drift: bool,
) -> None:
    trace = recorder()
    with pytest.raises(ModelOutputError):
        observe_request(
            scenario_case("payment").request,
            load_corpus(CORPUS).chunks,
            demo_access(),
            trace,
            model=DriftingModel(drift),
        )
    assert trace.records[-1].error_code == "model_contract"


def test_no_evidence_skips_model_and_missing_fact_is_not_a_runtime_exception() -> None:
    backend, trace = DriftingModel(False), recorder()
    result = observe_request(
        scenario_case("denied").request,
        load_corpus(CORPUS).chunks,
        demo_access(),
        trace,
        model=backend,
    )
    assert backend.calls == 0 and result.model is None
    assert (
        dict(trace.records[-1].attributes)["generation_mode"] == "skipped_no_evidence"
    )
    missing, missing_trace = run("missing-fact")
    assert "delivery date" not in missing.answer.lower()
    assert missing.retrieval.status == "evidence_available"
    assert missing_trace.records[-1].status == "ok"


def test_export_refuses_to_overwrite_existing_artifacts(tmp_path: Path) -> None:
    _, trace = run()
    destination = tmp_path / "run"
    save_trace(destination, trace.document())
    original = (destination / "trace.json").read_bytes()
    with pytest.raises(FileExistsError):
        save_trace(destination, {"replacement": True})
    assert (destination / "trace.json").read_bytes() == original


@pytest.mark.parametrize("capture", [False, True])
def test_cli_requires_explicit_synthetic_payload_capture(
    tmp_path: Path, capture: bool
) -> None:
    destination = tmp_path / "run"
    args = [
        sys.executable,
        "-m",
        "labs.week_10.demo",
        "--scenario",
        "model-fixture",
        "--output-dir",
        str(destination),
    ]
    if capture:
        args.append("--capture-synthetic-content")
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    assert json.loads(completed.stdout)["synthetic_content_saved"] is capture
    assert (destination / "synthetic-content.json").exists() is capture
    trace = json.loads((destination / "trace.json").read_text())
    assert trace["telemetry_complete"] is True
    assert "Net 30" not in json.dumps(trace)
