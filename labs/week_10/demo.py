"""Run controlled synthetic tracing scenarios; raw content capture is explicit."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from decimal import Decimal
import json
from pathlib import Path
from typing import Literal

from labs.week_07.retrieval import MetadataFilter, RetrievalRequest
from labs.week_08.data import demo_access, load_corpus
from labs.week_08.pipeline import PipelineConfig
from labs.week_10.generation import Completion, ModelIdentity, Prompt, RateCard, Usage
from labs.week_10.pipeline import ObservedResult, observe_request
from labs.week_10.tracing import TraceRecorder, deliver, failure_code

CORPUS = Path(__file__).parents[1] / "week_08" / "corpus.jsonl"
QUESTION = (
    "What payment condition controls Schedule A for the 1,000 kg copper-wire line?"
)
SCENARIOS = (
    "payment",
    "tight",
    "denied",
    "missing-fact",
    "bad-rewrite",
    "model-fixture",
    "model-timeout",
    "model-invalid",
)


@dataclass(frozen=True)
class FixtureModel:
    """Scripted text/counters, not inference or tokenizer measurements."""

    behavior: Literal["ok", "timeout", "invalid"] = "ok"
    identity: ModelIdentity = ModelIdentity("scripted-demo", "fixture-v1", "fixture")

    def generate(self, prompt: Prompt) -> Completion:
        if self.behavior == "timeout":
            raise TimeoutError(
                "synthetic provider details must stay out of routine traces"
            )
        text = (
            ""
            if self.behavior == "invalid"
            else "Invoice terms are Net 30 after inspection approval. [S1]"
        )
        return Completion(text, Usage(1000, 300, 0, "synthetic_fixture"))


def illustrative_prices() -> RateCard:
    """Invented arithmetic inputs, not a current provider price recommendation."""
    return RateCard(
        "illustrative-usd/v1", "USD", Decimal("2.00"), Decimal("8.00"), Decimal("0.50")
    )


@dataclass(frozen=True)
class DemoCase:
    request: RetrievalRequest
    rewrites: tuple[str, ...] = ()
    config: PipelineConfig = PipelineConfig()
    model: FixtureModel | None = None


def scenario_case(name: str) -> DemoCase:
    if name not in SCENARIOS:
        raise ValueError("unknown synthetic scenario")
    request = RetrievalRequest(
        "analyst",
        QUESTION,
        3,
        (MetadataFilter("document_type", "framework_agreement"),),
    )
    if name == "denied":
        request = RetrievalRequest("stranger", QUESTION, 3, request.filters)
    if name == "missing-fact":
        request = RetrievalRequest(
            "analyst",
            "What is the delivery date for CW-1000?",
            3,
            (
                MetadataFilter("document_type", "catalogue"),
                MetadataFilter("supplier", "Atlas Metals"),
            ),
        )
    if name == "bad-rewrite":
        return DemoCase(
            RetrievalRequest("analyst", "CW-1000 Net 30 after approval", 3),
            ("CW-1000 payment details",),
        )
    model = None
    if name.startswith("model-"):
        behavior: Literal["ok", "timeout", "invalid"] = (
            "timeout"
            if name == "model-timeout"
            else ("invalid" if name == "model-invalid" else "ok")
        )
        model = FixtureModel(behavior)
    return DemoCase(
        request,
        config=PipelineConfig(context_chars=300 if name == "tight" else 1400),
        model=model,
    )


def synthetic_content(
    case: DemoCase, observed: ObservedResult | None
) -> dict[str, object]:
    """Called only by this fixed-fixture demo's explicit content-capture option."""
    result = observed.retrieval if observed else None
    return {
        "scope": "explicit controlled synthetic demo content; not routine telemetry",
        "request": asdict(case.request),
        "reviewed_rewrites": case.rewrites,
        "planned_queries": observed.queries if observed else None,
        "retrieved": [
            {"chunk": asdict(c.chunk), "score": c.score, "rank": c.rank}
            for c in result.candidates
        ]
        if result
        else [],
        "reranked": [
            {
                "chunk_id": c.chunk.chunk_id,
                "score": c.score,
                "retrieval_rank": c.retrieval_rank,
            }
            for c in result.reranked
        ]
        if result
        else [],
        "context": json.loads(result.context) if result else None,
        "prompt": asdict(observed.model.prompt)
        if observed and observed.model
        else None,
        "model_response": observed.model.completion.text
        if observed and observed.model
        else None,
        "answer": observed.answer if observed else None,
    }


def save_trace(output_dir: Path, document: dict[str, object]) -> None:
    """Preserve earlier artifacts. A failed write is reported by deliver()."""
    output_dir.mkdir(parents=True, exist_ok=False)
    with (output_dir / "trace.json").open("x", encoding="utf-8") as handle:
        handle.write(
            json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=SCENARIOS, default="payment")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--capture-synthetic-content", action="store_true")
    args = parser.parse_args()
    case = scenario_case(args.scenario)
    chunks = load_corpus(CORPUS).chunks
    recorder = TraceRecorder("demo-" + args.scenario)
    observed = None
    error_code = None
    try:
        observed = observe_request(
            case.request,
            chunks,
            demo_access(),
            recorder,
            config=case.config,
            rewrites=case.rewrites,
            model=case.model,
            prices=illustrative_prices() if case.model else None,
        )
    except Exception as error:
        error_code = failure_code(error)
    delivery = deliver(recorder, lambda document: save_trace(args.output_dir, document))
    content_saved = False
    if delivery.delivered and args.capture_synthetic_content:
        with (args.output_dir / "synthetic-content.json").open(
            "x", encoding="utf-8"
        ) as handle:
            handle.write(
                json.dumps(
                    synthetic_content(case, observed),
                    ensure_ascii=False,
                    allow_nan=False,
                    indent=2,
                )
                + "\n"
            )
        content_saved = True
    print(
        json.dumps(
            {
                "scenario": args.scenario,
                "application_error": error_code,
                "outcome": observed.retrieval.status if observed else None,
                "model_fixture_observed": bool(observed and observed.model),
                "trace_delivered": delivery.delivered,
                "delivery_error": delivery.error_code,
                "synthetic_content_saved": content_saved,
            },
            indent=2,
        )
    )
    if error_code or not delivery.delivered:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
