"""Build deterministic candidate assessment banks for Weeks 21–28.

The script prints an apply_patch payload rather than writing repository files.
Run `python scripts/build_candidate_assessments.py 21 --patch` from the root and
apply the emitted patch. Candidate banks remain static assets for GitHub Pages.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Concept:
    term: str
    definition: str
    action: str
    limitation: str


@dataclass(frozen=True, slots=True)
class WeekConfig:
    title: str
    concepts: tuple[Concept, ...]


def _concept(term: str, definition: str, action: str, limitation: str) -> Concept:
    return Concept(term, definition, action, limitation)


def _concepts(
    rows: tuple[tuple[str, str, str, str], ...],
) -> tuple[Concept, ...]:
    return tuple(_concept(*row) for row in rows)


CONFIGS: dict[int, WeekConfig] = {
    21: WeekConfig(
        "Cost and latency optimisation",
        (
            _concept(
                "baseline",
                "the same workload measured before a change",
                "materialise identical requests for both strategies",
                "a changed workload invalidates the comparison",
            ),
            _concept(
                "model routing",
                "selecting a model from observable task needs",
                "route simple work small and escalate below the quality floor",
                "routing mistakes can trade quality for savings",
            ),
            _concept(
                "quality floor",
                "the minimum accepted evaluation result",
                "block or escalate work below the declared threshold",
                "a synthetic estimate is not production quality evidence",
            ),
            _concept(
                "token budget",
                "a finite allowance for input and output tokens",
                "reject or reshape work before it exceeds policy",
                "the model must not grant itself more budget",
            ),
            _concept(
                "optional context",
                "context declared safe to remove when necessary",
                "prune optional passages before required evidence",
                "misclassification can remove answer-changing evidence",
            ),
            _concept(
                "TTFT",
                "elapsed time until the first generated token",
                "measure it separately from full completion",
                "streaming may improve TTFT without reducing total work",
            ),
            _concept(
                "end-to-end latency",
                "elapsed time until the usable result completes",
                "include queue, model, validation and tool time",
                "averages can hide tail regressions",
            ),
            _concept(
                "critical path",
                "the longest dependent path through parallel work",
                "run only independent calls together and take group maxima",
                "parallel work increases simultaneous demand",
            ),
            _concept(
                "batching",
                "combining compatible requests for shared processing",
                "measure throughput and queue delay together",
                "large batches can worsen time to first token",
            ),
            _concept(
                "exact cache",
                "reuse only when every result-changing input matches",
                "key by tenant model prompt and data version",
                "an incomplete key can leak or return stale output",
            ),
            _concept(
                "semantic cache",
                "reuse based on measured meaning similarity",
                "evaluate false hits and apply authorization before reuse",
                "similar wording can still require a different answer",
            ),
            _concept(
                "prompt compression",
                "reducing context while preserving task information",
                "gate compression on downstream quality and safety",
                "a shorter prompt is not automatically better",
            ),
            _concept(
                "cost per completed task",
                "total spend divided by accepted completed outcomes",
                "include retries fallbacks and rejected work",
                "cost per call can hide failed journeys",
            ),
            _concept(
                "tail latency",
                "high-percentile delay such as p95 or p99",
                "compare tails by workload and cold or warm state",
                "median improvement can coexist with worse tails",
            ),
            _concept(
                "budget rejection",
                "a visible terminal state for work above policy",
                "return a controlled rejection before model execution",
                "silently truncating required work is not rejection",
            ),
        ),
    ),
    22: WeekConfig(
        "MCP and interoperable tools",
        (
            _concept(
                "host",
                "the user-facing application that owns policy and consent",
                "keep user experience and connection policy at the host",
                "the host does not replace server-side authorization",
            ),
            _concept(
                "client",
                "the protocol participant connecting one host to one server",
                "maintain a bounded trust relationship per server",
                "a client connection is not blanket tool permission",
            ),
            _concept(
                "server",
                "the component declaring and serving bounded capabilities",
                "validate identity inputs outputs and authority per request",
                "protocol compliance does not make a server safe",
            ),
            _concept(
                "tool",
                "a capability the model may select under host policy",
                "use a closed schema and authorize every invocation",
                "annotations are hints rather than enforcement",
            ),
            _concept(
                "resource",
                "read-only context selected by the application",
                "expose only bounded non-secret content",
                "a resource must not bypass tenant filtering",
            ),
            _concept(
                "prompt",
                "a named message template selected by a user",
                "treat it as convenience without added authority",
                "prompt text is not a security boundary",
            ),
            _concept(
                "discovery",
                "a way to learn a server capability catalog",
                "cache only according to declared hints and stable order",
                "discoverable does not mean authorized",
            ),
            _concept(
                "structured output",
                "a declared machine-validatable result schema",
                "return coherent status and data fields",
                "schema validity does not prove semantic truth",
            ),
            _concept(
                "tool annotation",
                "metadata describing properties such as read-only behavior",
                "use hints for planning and presentation",
                "a malicious client can ignore annotations",
            ),
            _concept(
                "trusted principal",
                "validated actor tenant and scopes from authentication",
                "bind it outside model-generated arguments",
                "the teaching lab does not implement authentication",
            ),
            _concept(
                "tenant isolation",
                "preventing one tenant from observing another tenant data",
                "filter every lookup by the trusted tenant",
                "an unscoped cache can break isolation",
            ),
            _concept(
                "audience binding",
                "accepting a token only at its intended resource",
                "validate issuer expiry signature and audience",
                "a valid token for another API is not valid here",
            ),
            _concept(
                "token passthrough",
                "forwarding an inbound token to another resource",
                "obtain a separate scoped downstream credential",
                "passthrough creates confused-deputy risk",
            ),
            _concept(
                "stateless request",
                "a self-describing request independent of a transport session",
                "carry explicit handles when application state is needed",
                "stateless protocol does not forbid application state",
            ),
            _concept(
                "transport test",
                "an interoperability check across the actual wire boundary",
                "connect an independent client over the deployed transport",
                "in-process calls do not prove framing or gateway behavior",
            ),
        ),
    ),
    23: WeekConfig(
        "GenAI system design",
        (
            _concept(
                "requirements",
                "users goals constraints non-goals and risk stated before components",
                "clarify scope traffic and consequence of error",
                "silent assumptions make the design brittle",
            ),
            _concept(
                "metrics",
                "measurable quality safety operations and cost outcomes",
                "define thresholds and segments before launch",
                "one average can hide severe subgroup failure",
            ),
            _concept(
                "data",
                "sources ownership freshness permissions retention and deletion",
                "trace ingestion and query-time data paths",
                "a vector store choice does not solve data governance",
            ),
            _concept(
                "architecture",
                "components flows state and trust boundaries",
                "show synchronous asynchronous and failure paths",
                "a diagram without contracts is incomplete",
            ),
            _concept(
                "retrieval and tools",
                "grounding and external capabilities with explicit contracts",
                "specify filters schemas timeouts authority and approvals",
                "tool access can create consequential side effects",
            ),
            _concept(
                "model choice",
                "selection based on task evidence and deployment constraints",
                "compare candidates on segmented evaluation and load",
                "brand popularity is not workload evidence",
            ),
            _concept(
                "evaluation",
                "repeatable offline and online evidence against acceptance gates",
                "version datasets judges prompts and thresholds",
                "a demo is not a release evaluation",
            ),
            _concept(
                "deployment",
                "controlled release versioning rollback and compatibility",
                "use canaries and a tested rollback trigger",
                "shipping without rollback turns regression into an incident",
            ),
            _concept(
                "monitoring",
                "signals connecting user quality and system health",
                "observe latency errors cost drift and unsafe outcomes",
                "logs alone do not define an SLO",
            ),
            _concept(
                "security",
                "identity authorization isolation validation and threat controls",
                "enforce least privilege at every tool and data boundary",
                "a system prompt cannot enforce access control",
            ),
            _concept(
                "cost",
                "capacity and economic estimates with explicit units",
                "calculate requests concurrency tokens and headroom",
                "unlabelled assumptions create false precision",
            ),
            _concept(
                "failure",
                "controlled behavior when dependencies data or releases fail",
                "define timeout fallback degradation reconciliation and alerting",
                "retrying every error can amplify outages",
            ),
            _concept(
                "trade-off",
                "an explicit benefit cost and rejected alternative",
                "state when the opposite choice would be better",
                "framework preference is not a trade-off",
            ),
            _concept(
                "critical path",
                "the dependent sequence controlling end-to-end latency",
                "sum sequential work and max independent branches",
                "parallel branches still consume capacity",
            ),
            _concept(
                "readiness gate",
                "a threshold that blocks progression when critical evidence is missing",
                "require requirements evaluation security cost and failure coverage",
                "a structural pass is not architecture approval",
            ),
        ),
    ),
    24: WeekConfig(
        "Project storytelling and mock interviews",
        (
            _concept(
                "evidence record",
                "one source of facts used by every story depth",
                "update evidence before changing the narrative",
                "recorded provenance still needs external verification",
            ),
            _concept(
                "situation",
                "the minimum context needed to understand the problem",
                "state users stakes and starting condition briefly",
                "too much setup hides candidate decisions",
            ),
            _concept(
                "task",
                "the outcome and constraints the team accepted",
                "separate requested result from implementation choice",
                "a vague task makes impact impossible to judge",
            ),
            _concept(
                "personal role",
                "work decisions and ownership attributable to the candidate",
                "separate I-owned work from team delivery",
                "overclaiming team work damages credibility",
            ),
            _concept(
                "action",
                "observable work personally performed",
                "name the decision implementation or coordination behavior",
                "a technology list is not an action",
            ),
            _concept(
                "metric provenance",
                "the source baseline window and attribution behind a number",
                "retain enough detail to defend measurement",
                "precision without provenance can mislead",
            ),
            _concept(
                "team attribution",
                "language that credits a shared outcome accurately",
                "say what I owned and what we achieved",
                "team results must not become individual claims",
            ),
            _concept(
                "decision evidence",
                "choice reason rejected alternative and consequence",
                "connect the choice to a requirement and test",
                "naming a framework does not justify it",
            ),
            _concept(
                "failure story",
                "a problem its detection response and resulting change",
                "describe controlled learning without blaming people",
                "a story with no setback may lack operational depth",
            ),
            _concept(
                "limitation",
                "a current boundary or unresolved weakness",
                "state it and the next evidence needed",
                "hiding limitations invites an avoidable credibility gap",
            ),
            _concept(
                "reflection",
                "what the candidate learned and would change",
                "connect learning to a concrete next action",
                "generic self-praise is not reflection",
            ),
            _concept(
                "two-minute story",
                "a concise problem role action result and limitation",
                "use it to earn focused follow-up questions",
                "it cannot contain every architecture detail",
            ),
            _concept(
                "ten-minute story",
                "a walkthrough adding decisions evaluation failure and leadership",
                "leave clear branches where an interviewer can interrupt",
                "a memorised monologue reduces interaction",
            ),
            _concept(
                "deep dive",
                "defensible detail for remaining actions metrics and operations",
                "follow interviewer questions back to evidence",
                "longer is not automatically deeper",
            ),
            _concept(
                "mock interview",
                "timed practice with adversarial evidence-based follow-ups",
                "record claims review gaps and repeat",
                "automated presence scoring cannot judge communication truth",
            ),
        ),
    ),
    25: WeekConfig(
        "Training foundations",
        _concepts(
            (
                (
                    "causal language modelling",
                    "predicting each next token from only earlier tokens",
                    "shift inputs and labels by one position",
                    "lower training loss does not prove useful generation",
                ),
                (
                    "cross-entropy loss",
                    "mean negative log probability assigned to target tokens",
                    "exclude padding and report comparable token sets",
                    "the scalar does not explain category-level failures",
                ),
                (
                    "document split",
                    "partitioning complete leakage groups before preprocessing",
                    "keep related documents wholly in train or validation",
                    "chunk-level random splitting can inflate validation",
                ),
                (
                    "training-only vocabulary",
                    "token mapping fitted without observing validation text",
                    "map unseen validation terms through declared unknown behavior",
                    "fitting on all data leaks held-out distribution information",
                ),
                (
                    "tokenisation",
                    "mapping text and special markers to stable token identifiers",
                    "pin and inspect the tokenizer and its revision",
                    "different token counts invalidate direct run comparisons",
                ),
                (
                    "optimiser",
                    "stateful rule converting gradients into parameter updates",
                    "record algorithm moments decay and update count",
                    "default hyperparameters are not universal evidence",
                ),
                (
                    "learning-rate warm-up",
                    "gradually increasing early update size",
                    "advance warm-up on optimiser steps",
                    "too much warm-up can waste a short run",
                ),
                (
                    "learning-rate decay",
                    "reducing later update size under a declared schedule",
                    "log the actual rate at every optimiser step",
                    "an incorrect step unit silently changes training",
                ),
                (
                    "gradient accumulation",
                    "combining micro-batch gradients before one update",
                    "normalise consistently and count global tokens",
                    "it does not make compute or stochastic behavior identical",
                ),
                (
                    "global token batch",
                    "tokens contributing to one distributed optimiser update",
                    "report devices micro-batch sequence length and accumulation",
                    "example count hides variable sequence lengths",
                ),
                (
                    "mixed precision",
                    "using lower precision for selected training compute and state",
                    "monitor finite loss gradients and hardware support",
                    "FP16 underflow can require loss scaling",
                ),
                (
                    "gradient clipping",
                    "bounding gradient norm before an optimiser update",
                    "log unclipped norms and clipped-step frequency",
                    "constant clipping may hide an unstable configuration",
                ),
                (
                    "validation loss",
                    "next-token loss on unchanged held-out documents",
                    "evaluate periodically without updating on validation",
                    "it is not a downstream task or safety score",
                ),
                (
                    "resumable checkpoint",
                    "weights plus all state required to continue the next update",
                    "save optimiser scheduler scaler random and data identities",
                    "weights alone do not reproduce exact continuation",
                ),
                (
                    "reproducible run",
                    "a run bound to immutable data code configuration and randomness",
                    "test an interrupted run against an uninterrupted control",
                    "a seed cannot compensate for changing inputs",
                ),
            )
        ),
    ),
    26: WeekConfig(
        "Data preparation",
        _concepts(
            (
                (
                    "licence gate",
                    "checking permitted training use retention and attribution",
                    "quarantine documents whose rights are unknown",
                    "public visibility does not imply training permission",
                ),
                (
                    "source provenance",
                    "traceable origin snapshot and processing history",
                    "retain stable IDs hashes and policy decisions",
                    "a URL alone may change or disappear",
                ),
                (
                    "normalisation",
                    "consistent text cleanup that preserves intended meaning",
                    "version Unicode whitespace and boilerplate rules",
                    "aggressive cleanup can destroy tables and numbers",
                ),
                (
                    "language filtering",
                    "accepting declared languages under a confidence policy",
                    "review short and mixed-language uncertainty",
                    "automatic detectors are probabilistic",
                ),
                (
                    "quality filtering",
                    "excluding malformed repetitive or unusable records",
                    "emit rejection reasons and inspect samples",
                    "one heuristic score is not an objective truth label",
                ),
                (
                    "exact deduplication",
                    "removing identical normalised content by fingerprint",
                    "deduplicate across all candidate partitions",
                    "exact hashes miss small edits and paraphrases",
                ),
                (
                    "near deduplication",
                    "detecting highly similar documents or passages",
                    "validate thresholds on domain examples",
                    "over-aggressive matching can remove distinct facts",
                ),
                (
                    "contamination",
                    "training exposure to evaluation questions answers or variants",
                    "compare held-out fingerprints before the final split",
                    "no match does not prove absence of contamination",
                ),
                (
                    "PII minimisation",
                    "avoiding collection of unnecessary personal information",
                    "remove sensitive fields before derived datasets",
                    "redaction after copying does not erase earlier snapshots",
                ),
                (
                    "PII redaction",
                    "replacing detected identifiers while preserving safe structure",
                    "measure detection coverage and deletion propagation",
                    "email and phone regexes are incomplete",
                ),
                (
                    "source mixing",
                    "controlling accepted token contribution from each source",
                    "declare caps or weights and inspect representation",
                    "large repetitive sources can dominate behavior",
                ),
                (
                    "grouped split",
                    "keeping related documents in a single partition",
                    "group by source family entity or time boundary",
                    "random chunks can leak near copies",
                ),
                (
                    "sequence packing",
                    "combining short examples into bounded token sequences",
                    "preserve boundaries masks and attention policy",
                    "silent truncation can remove answers or delimiters",
                ),
                (
                    "dataset manifest",
                    "versioned inventory of inputs rules outputs and statistics",
                    "hash configuration and cleaned records",
                    "a manifest is not proof of legal approval",
                ),
                (
                    "rejection evidence",
                    "counts and safe samples explaining excluded records",
                    "monitor each policy reason across versions",
                    "silent drops make bias and failures invisible",
                ),
            )
        ),
    ),
    27: WeekConfig(
        "Fine-tuning and LoRA",
        _concepts(
            (
                (
                    "full fine-tuning",
                    "updating every trainable weight of the base model",
                    "measure domain gain retained capability and full memory",
                    "high flexibility increases compute and forgetting risk",
                ),
                (
                    "parameter-efficient fine-tuning",
                    "adapting behavior through a small trainable parameter subset",
                    "store adapter configuration with the base identity",
                    "fewer trainable weights do not guarantee quality",
                ),
                (
                    "LoRA",
                    "a low-rank learned update applied to frozen weights",
                    "train only A and B adapter factors",
                    "poor targets or rank can underfit the task",
                ),
                (
                    "LoRA rank",
                    "the dimensional capacity of the low-rank update",
                    "compare ranks under the same data and evaluation",
                    "higher rank costs more and is not always better",
                ),
                (
                    "LoRA alpha",
                    "the numerator controlling adapter update scale",
                    "report alpha together with rank and effective scale",
                    "alpha cannot be interpreted without scaling convention",
                ),
                (
                    "target modules",
                    "base layers selected to receive adapters",
                    "map names to the exact model architecture",
                    "copied module defaults can miss important pathways",
                ),
                (
                    "zero-impact initialisation",
                    "initial adapters that leave base output unchanged",
                    "start one factor at zero and verify the first forward pass",
                    "incorrect initialisation can alter the baseline immediately",
                ),
                (
                    "QLoRA",
                    "training adapters while storing the frozen base quantised",
                    "declare quantisation format compute and adapter dtypes",
                    "it is not the same as exporting quantised inference weights",
                ),
                (
                    "quantised base",
                    "low-bit frozen weights dequantised for supported compute",
                    "measure real kernel memory quality and throughput",
                    "weight bytes alone omit activations and optimiser state",
                ),
                (
                    "training stability",
                    "finite controlled optimisation across the planned run",
                    "monitor loss gradients learning rate and checkpoints",
                    "a completed process can still have numerical failure",
                ),
                (
                    "catastrophic forgetting",
                    "domain adaptation that damages previously useful capability",
                    "retain general and safety suites beside domain evaluation",
                    "domain-only scores cannot detect the regression",
                ),
                (
                    "adapter artefact",
                    "separable learned weights requiring a compatible base",
                    "version base tokenizer template and adapter together",
                    "an adapter may fail against a different revision",
                ),
                (
                    "domain baseline",
                    "unchanged test performance of the base or prompted base",
                    "freeze cases before training and reuse them fairly",
                    "training examples are not a held-out baseline",
                ),
                (
                    "early stopping",
                    "selecting a checkpoint from held-out progress",
                    "stop after declared non-improvement patience",
                    "selecting on test data leaks evaluation",
                ),
                (
                    "seed variance",
                    "performance changes caused by small-data randomness",
                    "repeat important runs and report dispersion",
                    "one successful seed can overstate reliability",
                ),
            )
        ),
    ),
    28: WeekConfig(
        "Instruction tuning",
        _concepts(
            (
                (
                    "instruction-response example",
                    "a traceable request paired with the intended answer",
                    "store category source rights and review status",
                    "fluent synthetic answers can still be wrong",
                ),
                (
                    "behavior specification",
                    "declared tasks formats refusals and escalation expectations",
                    "define categories and release metrics before data creation",
                    "a loose conversation collection can blur the target",
                ),
                (
                    "chat template",
                    "model-specific rendering of roles and special tokens",
                    "pin and unit-test the training and inference template",
                    "wrong or doubled tokens can degrade behavior",
                ),
                (
                    "supervised fine-tuning",
                    "optimising model outputs against labelled response tokens",
                    "train on reviewed examples and evaluate unseen groups",
                    "low training loss can reflect memorisation",
                ),
                (
                    "response-only loss",
                    "loss applied to assistant answer tokens rather than prompts",
                    "inspect token labels and masks after truncation",
                    "a malformed mask can train the wrong role or no tokens",
                ),
                (
                    "padding mask",
                    "zero attention or loss contribution for padding positions",
                    "verify alignment for every padded batch",
                    "padding in loss distorts optimisation and metrics",
                ),
                (
                    "dataset diversity",
                    "coverage across tasks lengths difficulty outcomes and language",
                    "measure category balance and inspect tail cases",
                    "surface rewrites do not create real scenario diversity",
                ),
                (
                    "source-group split",
                    "partitioning all variants from one source together",
                    "split before model-dependent preprocessing",
                    "template variants across partitions leak answers",
                ),
                (
                    "instruction deduplication",
                    "removing exact and near duplicate request-answer pairs",
                    "compare normalised pairs before splitting",
                    "exact matching misses paraphrases",
                ),
                (
                    "response schema",
                    "machine-checkable structure required from an answer",
                    "validate training labels with the inference schema",
                    "valid structure does not prove factual correctness",
                ),
                (
                    "explicit truncation policy",
                    "declared handling for examples above token limits",
                    "reject revise or record intentional truncation",
                    "silent cuts can remove the answer or closing syntax",
                ),
                (
                    "example packing",
                    "placing multiple bounded examples in one training sequence",
                    "preserve roles boundaries attention and loss masks",
                    "cross-example attention may change the task",
                ),
                (
                    "memorisation baseline",
                    "a lookup showing performance on exact seen instructions",
                    "compare it with unseen-source validation",
                    "perfect training recall is not generalisation",
                ),
                (
                    "overfitting",
                    "training improvement paired with stagnant or worse held-out behavior",
                    "track task metrics by unseen category and source",
                    "training loss alone cannot diagnose it",
                ),
                (
                    "inference parity",
                    "matching template tokenizer schema and stop rules at serving",
                    "test one sample end to end with the deployed stack",
                    "train-serve mismatch can erase apparent gains",
                ),
            )
        ),
    ),
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _single_questions(week: int, config: WeekConfig) -> list[dict[str, object]]:
    questions: list[dict[str, object]] = []
    for index, concept in enumerate(config.concepts):
        questions.append(
            {
                "type": "single",
                "topic": concept.term,
                "difficulty": "foundation",
                "prompt": f"Which description best defines {concept.term} in Week {week}?",
                "explanation": f"{concept.term} means {concept.definition}; the distinction keeps the decision inspectable.",
                "options": [
                    {"id": "o1", "text": concept.definition},
                    {
                        "id": "o2",
                        "text": "an undocumented shortcut that always improves every workload",
                    },
                    {
                        "id": "o3",
                        "text": "a permission automatically granted to any connected model",
                    },
                    {
                        "id": "o4",
                        "text": "a production guarantee created by one local test",
                    },
                ],
                "correct": ["o1"],
            }
        )
        questions.append(
            {
                "type": "single",
                "topic": concept.term,
                "difficulty": "applied",
                "prompt": f"Scenario {index + 1}: which action applies {concept.term} most defensibly?",
                "explanation": f"The lesson applies {concept.term} by requiring the team to {concept.action}; its limit remains visible.",
                "options": [
                    {"id": "o1", "text": concept.action},
                    {
                        "id": "o2",
                        "text": "hide the boundary so the output appears simpler",
                    },
                    {
                        "id": "o3",
                        "text": "let model-generated text decide its own authority",
                    },
                    {
                        "id": "o4",
                        "text": "claim production readiness without workload evidence",
                    },
                ],
                "correct": ["o1"],
            }
        )
    return questions


def _multiple_questions(week: int, config: WeekConfig) -> list[dict[str, object]]:
    questions: list[dict[str, object]] = []
    for index in range(20):
        concept = config.concepts[index % len(config.concepts)]
        questions.append(
            {
                "type": "multiple",
                "topic": concept.term,
                "difficulty": "foundation" if index < 5 else "applied",
                "prompt": f"Which three statements form a sound {concept.term} contract in Week {week} practice case {index + 1}?",
                "explanation": f"A sound answer defines the concept, applies {concept.action}, and keeps this limit visible: {concept.limitation}.",
                "options": [
                    {"id": "o1", "text": concept.definition},
                    {"id": "o2", "text": concept.action},
                    {
                        "id": "o3",
                        "text": f"Keep this limitation visible: {concept.limitation}",
                    },
                    {
                        "id": "o4",
                        "text": "Treat a framework label as sufficient evidence",
                    },
                    {
                        "id": "o5",
                        "text": "Remove authorization and failure checks to reduce latency",
                    },
                ],
                "correct": ["o1", "o2", "o3"],
            }
        )
    return questions


def _match_questions(week: int, config: WeekConfig) -> list[dict[str, object]]:
    questions: list[dict[str, object]] = []
    for index in range(15):
        selected = tuple(
            config.concepts[(index * 4 + offset) % len(config.concepts)]
            for offset in range(4)
        )
        questions.append(
            {
                "type": "match",
                "topic": "Concept mapping",
                "difficulty": "foundation" if index < 9 else "applied",
                "prompt": f"Match the Week {week} concepts to their boundaries in mapping set {index + 1}.",
                "explanation": "Correct mapping separates related ideas so the candidate can choose the right control and state its limitation.",
                "left": [
                    {"id": f"l{offset + 1}", "text": concept.term}
                    for offset, concept in enumerate(selected)
                ],
                "right": [
                    {"id": f"r{offset + 1}", "text": concept.definition}
                    for offset, concept in enumerate(selected)
                ],
                "correct": {f"l{offset}": f"r{offset}" for offset in range(1, 5)},
            }
        )
    return questions


def _short_questions(week: int, config: WeekConfig) -> list[dict[str, object]]:
    return [
        {
            "type": "short",
            "topic": concept.term,
            "difficulty": "foundation" if index < 10 else "applied",
            "prompt": f"Write the exact Week {week} term for this definition: {concept.definition}.",
            "explanation": f"The exact term is {concept.term}; use it when discussing this boundary and its evidence.",
            "accepted": [concept.term],
            "case_sensitive": False,
        }
        for index, concept in enumerate(config.concepts)
    ]


def _raises_checks(function: str, valid_call: str) -> list[dict[str, str]]:
    return [
        {"label": "Valid contract", "code": valid_call},
        {"label": "Deterministic repeat", "code": valid_call + "\n" + valid_call},
        {
            "label": "Reject boolean coercion",
            "code": f"assert raises((TypeError,ValueError),{function},True)",
        },
        {
            "label": "Reject missing input",
            "code": f"assert raises((TypeError,ValueError),{function},None)",
        },
        {
            "label": "Reject container input",
            "code": f"assert raises((TypeError,ValueError),{function},[])",
        },
    ]


def _code_question(index: int, concept: Concept) -> dict[str, object]:
    base = f"{_slug(concept.term)}_{index + 1}"
    template = index % 5
    if template == 0:
        name = f"select_{base}"
        prompt = f"Implement {name}(value). Require an exact non-blank string. Return value when it is 'accept' or 'revise'; otherwise return 'unknown'."
        reference = f"def {name}(value):\n    if type(value) is not str: raise TypeError('value_invalid')\n    if not value.strip(): raise ValueError('value_blank')\n    return value if value in {{'accept','revise'}} else 'unknown'\n"
        checks = [
            {"label": "Accepted state", "code": f"assert {name}('accept')=='accept'"},
            {"label": "Revision state", "code": f"assert {name}('revise')=='revise'"},
            {"label": "Unknown state", "code": f"assert {name}('other')=='unknown'"},
            {
                "label": "Blank rejected",
                "code": f"assert raises(ValueError,{name},'  ')",
            },
            {
                "label": "Strict string",
                "code": f"assert raises(TypeError,{name},True) and raises(TypeError,{name},1)",
            },
        ]
    elif template == 1:
        name = f"scope_{base}"
        prompt = f"Implement {name}(tenant, version, item). Require three exact non-blank strings and return the tuple (tenant, version, item)."
        reference = f"def {name}(tenant,version,item):\n    values=(tenant,version,item)\n    if any(type(value) is not str for value in values): raise TypeError('scope_invalid')\n    if any(not value.strip() for value in values): raise ValueError('scope_blank')\n    return values\n"
        checks = [
            {
                "label": "Scope order",
                "code": f"assert {name}('t1','v2','i3')==('t1','v2','i3')",
            },
            {
                "label": "Tenant retained",
                "code": f"assert {name}('t2','v2','i3')[0]=='t2'",
            },
            {
                "label": "Version retained",
                "code": f"assert {name}('t1','v9','i3')[1]=='v9'",
            },
            {
                "label": "Blank rejected",
                "code": f"assert raises(ValueError,{name},'t1','','i3')",
            },
            {
                "label": "Strict strings",
                "code": f"assert raises(TypeError,{name},'t1',2,'i3')",
            },
        ]
    elif template == 2:
        name = f"missing_{base}"
        prompt = f"Implement {name}(required, present). Require tuples of unique non-blank strings. Return required items absent from present, preserving required order."
        reference = f"def {name}(required,present):\n    if type(required) is not tuple or type(present) is not tuple: raise TypeError('container_invalid')\n    if any(type(value) is not str for value in required+present): raise TypeError('item_invalid')\n    if any(not value.strip() for value in required+present): raise ValueError('item_blank')\n    if len(set(required))!=len(required) or len(set(present))!=len(present): raise ValueError('duplicate')\n    return tuple(value for value in required if value not in present)\n"
        checks = [
            {
                "label": "Find missing",
                "code": f"assert {name}(('a','b','c'),('a','c'))==('b',)",
            },
            {
                "label": "Preserve order",
                "code": f"assert {name}(('c','a','b'),('x',))==('c','a','b')",
            },
            {
                "label": "Complete set",
                "code": f"assert {name}(('a','b'),('b','a'))==()",
            },
            {
                "label": "Duplicates rejected",
                "code": f"assert raises(ValueError,{name},('a','a'),())",
            },
            {
                "label": "Strict tuples",
                "code": f"assert raises(TypeError,{name},['a'],()) and raises(TypeError,{name},('a',),(1,))",
            },
        ]
    elif template == 3:
        name = f"bounded_{base}"
        prompt = f"Implement {name}(values, cap). Require a tuple of exact non-negative ints and a positive exact-int cap. Return min(sum(values), cap)."
        reference = f"def {name}(values,cap):\n    if type(values) is not tuple or type(cap) is not int: raise TypeError('input_invalid')\n    if type(cap) is bool or cap<=0: raise ValueError('cap_invalid')\n    if any(type(value) is not int or type(value) is bool for value in values): raise TypeError('value_invalid')\n    if any(value<0 for value in values): raise ValueError('negative')\n    return min(sum(values),cap)\n"
        checks = [
            {"label": "Sum below cap", "code": f"assert {name}((2,3),10)==5"},
            {"label": "Cap applied", "code": f"assert {name}((8,9),10)==10"},
            {"label": "Empty tuple", "code": f"assert {name}((),10)==0"},
            {
                "label": "Negative rejected",
                "code": f"assert raises(ValueError,{name},(1,-1),10)",
            },
            {
                "label": "Strict integers",
                "code": f"assert raises(TypeError,{name},(True,),10) and raises(ValueError,{name},(),0)",
            },
        ]
    else:
        name = f"gate_{base}"
        prompt = f"Implement {name}(scores, threshold). Require a non-empty tuple of exact ints from 0 to 100 and an exact-int threshold in that range. Return True only when every score meets threshold."
        reference = f"def {name}(scores,threshold):\n    if type(scores) is not tuple or type(threshold) is not int or type(threshold) is bool: raise TypeError('input_invalid')\n    if not scores: raise ValueError('scores_empty')\n    if threshold<0 or threshold>100: raise ValueError('threshold_invalid')\n    if any(type(score) is not int or type(score) is bool for score in scores): raise TypeError('score_invalid')\n    if any(score<0 or score>100 for score in scores): raise ValueError('score_range')\n    return all(score>=threshold for score in scores)\n"
        checks = [
            {"label": "Gate passes", "code": f"assert {name}((80,90,100),80) is True"},
            {"label": "Gate blocks", "code": f"assert {name}((80,79,100),80) is False"},
            {
                "label": "Boundary accepted",
                "code": f"assert {name}((0,),0) is True and {name}((100,),100) is True",
            },
            {
                "label": "Empty rejected",
                "code": f"assert raises(ValueError,{name},(),50)",
            },
            {
                "label": "Strict range",
                "code": f"assert raises(TypeError,{name},(True,),50) and raises(ValueError,{name},(101,),50)",
            },
        ]
    return {
        "type": "code",
        "topic": concept.term,
        "difficulty": "foundation" if index < 5 else "applied",
        "prompt": prompt
        + f" Use it as a small deterministic exercise for {concept.term}.",
        "explanation": f"The function practises an inspectable boundary related to {concept.term}: {concept.action}. It is intentionally standard-library only.",
        "starter": f"def {name}(*args, **kwargs):\n    raise NotImplementedError('Implement the stated contract')\n",
        "reference": reference,
        "checks": checks,
    }


def build_bank(week: int) -> dict[str, object]:
    config = CONFIGS[week]
    questions = (
        _single_questions(week, config)
        + _multiple_questions(week, config)
        + _match_questions(week, config)
        + _short_questions(week, config)
        + [
            _code_question(index, config.concepts[index % len(config.concepts)])
            for index in range(20)
        ]
    )
    for index, question in enumerate(questions, 1):
        question["id"] = f"W{week:02d}-Q{index:03d}"
    return {
        "schema_version": 1,
        "week": week,
        "version": "1.0.0",
        "title": config.title,
        "code_language": "python",
        "paper_policy": {
            "questions": 10,
            "per_type": 2,
            "points_each": 10,
            "difficulty_per_type": {
                kind: {"foundation": 1, "applied": 1}
                for kind in ("single", "multiple", "match", "short", "code")
            },
        },
        "questions": questions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("week", type=int, choices=tuple(CONFIGS))
    parser.add_argument("--patch", action="store_true")
    args = parser.parse_args()
    payload = json.dumps(
        build_bank(args.week), ensure_ascii=True, separators=(",", ":")
    )
    if args.patch:
        lines = "\n".join(f"+{line}" for line in payload.splitlines())
        target = Path.cwd() / "assessments" / f"week-{args.week:02d}.json"
        print(f"*** Begin Patch\n*** Add File: {target}\n{lines}\n*** End Patch")
    else:
        print(payload)


if __name__ == "__main__":
    main()
