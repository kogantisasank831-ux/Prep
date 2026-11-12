"""Six synthetic GenAI system-design interview cases."""

from __future__ import annotations

from labs.week_23.models import CaseId, DesignCase


CASES: dict[CaseId, DesignCase] = {
    "enterprise-rag": DesignCase(
        case_id="enterprise-rag",
        title="Enterprise knowledge assistant with citations",
        goal="Answer employee questions from permissioned internal documents with inspectable citations and abstention.",
        constraints=(
            "Twenty thousand active employees across isolated business units.",
            "Document permissions can change after indexing.",
            "The p95 answer latency target is three seconds.",
        ),
        risk_focus=("permission drift", "unsupported answers", "stale documents"),
    ),
    "procurement-agent": DesignCase(
        case_id="procurement-agent",
        title="Approval-bound procurement agent",
        goal="Draft sourcing actions and execute only explicitly approved, policy-compliant supplier operations.",
        constraints=(
            "Writes can have contractual consequences.",
            "Every action needs tenant isolation and an audit trail.",
            "Provider and supplier APIs fail independently.",
        ),
        risk_focus=("excess authority", "duplicate writes", "prompt injection"),
    ),
    "support-copilot": DesignCase(
        case_id="support-copilot",
        title="Real-time customer-support copilot",
        goal="Suggest grounded replies and next actions while an agent handles a live customer conversation.",
        constraints=(
            "First suggestions should arrive within one second.",
            "Customer data must remain region-bound.",
            "Recommendations cannot silently change an account.",
        ),
        risk_focus=("latency", "privacy", "unsafe recommendations"),
    ),
    "document-intelligence": DesignCase(
        case_id="document-intelligence",
        title="Multimodal contract-intelligence pipeline",
        goal="Extract clauses and tables from varied contract files with traceable evidence and human review.",
        constraints=(
            "Scans, native PDFs and spreadsheets share one intake queue.",
            "Low-confidence fields require manual verification.",
            "Reprocessing must not duplicate downstream records.",
        ),
        risk_focus=("OCR error", "schema drift", "duplicate processing"),
    ),
    "local-model-gateway": DesignCase(
        case_id="local-model-gateway",
        title="Cost-aware local model gateway",
        goal="Route mixed classification and generation traffic across local models while preserving quality and deadlines.",
        constraints=(
            "Two shared GPUs serve bursty internal workloads.",
            "Some requests contain regulated data.",
            "Quality regressions must block a model rollout.",
        ),
        risk_focus=("GPU saturation", "routing quality", "data residency"),
    ),
    "agent-evaluation-platform": DesignCase(
        case_id="agent-evaluation-platform",
        title="Continuous agent evaluation platform",
        goal="Compare agent releases with reproducible task, safety, latency and cost evidence before deployment.",
        constraints=(
            "Evaluation data includes private production-derived cases.",
            "Nondeterministic outputs need repeated trials.",
            "Judge-model changes cannot silently rewrite historical baselines.",
        ),
        risk_focus=("data leakage", "judge drift", "benchmark gaming"),
    ),
}


def get_case(case_id: CaseId) -> DesignCase:
    """Return one immutable interview case."""

    return CASES[case_id]
