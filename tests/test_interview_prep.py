from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ROLE_BANKS = {
    "AIE": ROOT / "interview-prep/roles/agentic-ai-engineer.md",
    "DSTL": ROOT / "interview-prep/roles/data-science-technical-lead.md",
    "SDS": ROOT / "interview-prep/roles/senior-data-scientist.md",
}

BATCH_ONE_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/python.md",
    ROOT / "interview-prep/cheat-sheets/sql.md",
    ROOT / "interview-prep/cheat-sheets/probability-statistics.md",
    ROOT / "interview-prep/cheat-sheets/machine-learning.md",
)

BATCH_TWO_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/deep-learning-neural-networks.md",
    ROOT / "interview-prep/cheat-sheets/nlp.md",
    ROOT / "interview-prep/cheat-sheets/transformers.md",
    ROOT / "interview-prep/cheat-sheets/llm-generative-ai.md",
)

BATCH_THREE_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/embeddings-vector-search.md",
    ROOT / "interview-prep/cheat-sheets/document-ingestion-chunking-indexing.md",
    ROOT / "interview-prep/cheat-sheets/rag-architecture-retrieval-generation.md",
    ROOT / "interview-prep/cheat-sheets/rag-evaluation-security-production.md",
)

BATCH_FOUR_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns.md",
    ROOT / "interview-prep/cheat-sheets/langgraph-deep-dive.md",
    ROOT / "interview-prep/cheat-sheets/agent-frameworks-libraries-comparison.md",
    ROOT / "interview-prep/cheat-sheets/agent-protocols-reliability-evaluation.md",
)

BATCH_FIVE_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/ai-ml-system-design-production-architecture.md",
    ROOT / "interview-prep/cheat-sheets/llm-inference-serving-optimization.md",
    ROOT / "interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle.md",
    ROOT / "interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity.md",
)

BATCH_SIX_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/data-distributed-compute-engineering.md",
    ROOT / "interview-prep/cheat-sheets/ai-security-privacy-governance.md",
    ROOT / "interview-prep/cheat-sheets/ai-technical-leadership-product-thinking.md",
    ROOT / "interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview.md",
)

BATCH_SEVEN_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/linear-algebra-calculus-optimization.md",
    ROOT / "interview-prep/cheat-sheets/experimentation-causal-inference.md",
    ROOT / "interview-prep/cheat-sheets/data-preparation-eda-feature-engineering.md",
    ROOT / "interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection.md",
)

BATCH_EIGHT_UPDATED_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/experimentation-causal-inference.md",
    ROOT / "interview-prep/cheat-sheets/data-preparation-eda-feature-engineering.md",
)

BATCH_EIGHT_NEW_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/time-series-forecasting.md",
    ROOT / "interview-prep/cheat-sheets/recommendation-search-ranking.md",
)

BATCH_EIGHT_CHEAT_SHEETS = (
    BATCH_EIGHT_UPDATED_CHEAT_SHEETS + BATCH_EIGHT_NEW_CHEAT_SHEETS
)

BATCH_NINE_UPDATED_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/linear-algebra-calculus-optimization.md",
)

BATCH_NINE_NEW_CHEAT_SHEETS = (
    ROOT
    / "interview-prep/cheat-sheets/unsupervised-learning-dimensionality-reduction.md",
    ROOT / "interview-prep/cheat-sheets/anomaly-detection-rare-event-modeling.md",
    ROOT
    / "interview-prep/cheat-sheets/explainability-fairness-uncertainty-model-governance.md",
)

BATCH_NINE_CHEAT_SHEETS = BATCH_NINE_UPDATED_CHEAT_SHEETS + BATCH_NINE_NEW_CHEAT_SHEETS

SPECIALIZED_MODELING_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/computer-vision-multimodal-ai.md",
    ROOT / "interview-prep/cheat-sheets/graph-machine-learning-gnn.md",
    ROOT / "interview-prep/cheat-sheets/survival-analysis-reliability-modeling.md",
    ROOT / "interview-prep/cheat-sheets/operations-research-scheduling-optimization.md",
)

AI_ENGINEERING_PLATFORM_CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/ai-backend-api-async-service-engineering.md",
    ROOT / "interview-prep/cheat-sheets/cloud-kubernetes-gpu-platform-engineering.md",
    ROOT / "interview-prep/cheat-sheets/ai-testing-release-quality-engineering.md",
    ROOT / "interview-prep/cheat-sheets/end-to-end-ai-architecture-mock-interview.md",
)

NEW_IMPORTED_CHEAT_SHEETS = (
    SPECIALIZED_MODELING_CHEAT_SHEETS + AI_ENGINEERING_PLATFORM_CHEAT_SHEETS
)

ALL_CHEAT_SHEETS = (
    BATCH_ONE_CHEAT_SHEETS
    + BATCH_TWO_CHEAT_SHEETS
    + BATCH_THREE_CHEAT_SHEETS
    + BATCH_FOUR_CHEAT_SHEETS
    + BATCH_FIVE_CHEAT_SHEETS
    + BATCH_SIX_CHEAT_SHEETS
    + BATCH_SEVEN_CHEAT_SHEETS
    + BATCH_EIGHT_NEW_CHEAT_SHEETS
    + BATCH_NINE_NEW_CHEAT_SHEETS
    + NEW_IMPORTED_CHEAT_SHEETS
)

CANONICAL_SOURCE_CHEAT_SHEETS = tuple(
    path
    for path in ALL_CHEAT_SHEETS
    if path.name != "unsupervised-learning-anomaly-detection.md"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def page_status(content: str) -> str:
    match = re.search(r'^status: "([^"]+)"$', content, re.MULTILINE)
    assert match is not None
    return match.group(1)


def markdown_h1_lines_outside_fences(content: str) -> list[str]:
    fence: str | None = None
    headings: list[str] = []
    for line in content.splitlines():
        stripped = line.lstrip()
        marker = next(
            (
                candidate
                for candidate in ("```", "~~~")
                if stripped.startswith(candidate)
            ),
            None,
        )
        if marker is not None:
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is None and line.startswith("# "):
            headings.append(line)
    return headings


def test_public_pages_have_required_front_matter() -> None:
    approved_pages = (
        ROOT / "interview-prep/master-index.md",
        ROOT / "interview-prep/index.md",
        ROOT / "cheat-sheets/index.md",
        ROOT / "interview-room/index.md",
        *ALL_CHEAT_SHEETS,
        *ROLE_BANKS.values(),
    )
    pages = approved_pages
    permalinks: list[str] = []
    for page in pages:
        content = read(page)
        assert content.startswith("---\n")
        assert 'layout: "week"' in content
        match = re.search(r'^permalink: "([^"]+)"$', content, re.MULTILINE)
        assert match is not None, page
        permalinks.append(match.group(1))
    assert all(page_status(read(page)) == "approved" for page in approved_pages)
    assert len(permalinks) == len(set(permalinks))


def test_role_banks_have_stable_complete_batches() -> None:
    for prefix, path in ROLE_BANKS.items():
        content = read(path)
        for batch in (1, 2, 3, 4, 5, 6, 7, 8, 9):
            ids = re.findall(
                rf"^### ({prefix}-B{batch}-\d{{2}}) — ",
                content,
                re.MULTILINE,
            )
            expected = [f"{prefix}-B{batch}-{index:02d}" for index in range(1, 21)]
            assert ids == expected
            assert len(ids) == len(set(ids)) == 20
        assert content.count("**Strong answer signals**") == 180
        assert content.count("**Follow-up probe:**") == 180
        assert content.count("**Revision links:**") == 180
        assert "question_count: 180" in content


def test_cheat_sheets_keep_their_rapid_revision_contract() -> None:
    for path in ALL_CHEAT_SHEETS:
        content = read(path)
        assert "## 1. Thirty-second revision" in content
        assert markdown_h1_lines_outside_fences(content) == []


def test_cheat_sheet_hub_links_the_complete_40_sheet_source_collection() -> None:
    hub = read(ROOT / "cheat-sheets/index.md")
    assert len(CANONICAL_SOURCE_CHEAT_SHEETS) == 40
    for path in CANONICAL_SOURCE_CHEAT_SHEETS:
        match = re.search(r'^permalink: "([^"]+)"$', read(path), re.MULTILINE)
        assert match is not None, path
        assert match.group(1) in hub, path
    assert "cdd45b6b0c08c5d88a626e4d16853abdf285f08d" in hub


def test_cheat_sheet_hub_has_search_filters_and_local_progress() -> None:
    hub = read(ROOT / "cheat-sheets/index.md")
    layout = read(ROOT / "_layouts/week.html")
    script = read(ROOT / "cheat-sheets.js")
    stylesheet = read(ROOT / "week.css")
    workflow = read(ROOT / ".github/workflows/weekly-assessments.yml")

    assert 'version: "1.1.0"' in hub
    for control_id in (
        "cheat-sheet-search",
        "cheat-sheet-batch",
        "cheat-sheet-progress-filter",
        "clear-cheat-sheet-filters",
        "cheat-sheet-progress",
        "reset-cheat-sheet-progress",
        "cheat-sheet-filter-status",
    ):
        assert f'id="{control_id}"' in hub
    for batch in range(1, 11):
        assert f'<option value="{batch}">Batch {batch} ·' in hub

    assert "page.url == '/cheat-sheets/'" in layout
    assert "'/cheat-sheets.js' | relative_url" in layout
    assert "applied-genai-cheat-sheets-v1" in script
    assert "localStorage" in script
    assert "textContent" in script
    assert ".innerHTML" not in script
    assert ".cheat-sheet-tools" in stylesheet
    assert "tests/test_cheat_sheets.mjs" in workflow


def test_new_cheat_sheets_preserve_source_provenance() -> None:
    for path in NEW_IMPORTED_CHEAT_SHEETS:
        content = read(path)
        assert (
            'source_repository: "kogantisasank831-ux/transformer-explainer"' in content
        )
        assert 'source_commit: "cdd45b6b0c08c5d88a626e4d16853abdf285f08d"' in content
        assert 'source_path: "AI_Data_Science_Interview_Cheat_Sheets/' in content


def test_public_interview_docs_reference_complete_weekly_curriculum() -> None:
    public_pages = (
        ROOT / "interview-prep/index.md",
        ROOT / "interview-prep/master-index.md",
        ROOT / "cheat-sheets/index.md",
        *ALL_CHEAT_SHEETS,
    )
    for path in public_pages:
        content = read(path)
        assert "Week 1–20" not in content, path
        assert "Week 1-20" not in content, path


def test_hub_links_every_interview_artifact() -> None:
    hub = read(ROOT / "interview-prep/index.md")
    required_paths = (
        "/interview-prep/master-index/",
        "/interview-prep/cheat-sheets/python/",
        "/interview-prep/cheat-sheets/sql/",
        "/interview-prep/cheat-sheets/probability-statistics/",
        "/interview-prep/cheat-sheets/machine-learning/",
        "/interview-prep/cheat-sheets/deep-learning-neural-networks/",
        "/interview-prep/cheat-sheets/nlp/",
        "/interview-prep/cheat-sheets/transformers/",
        "/interview-prep/cheat-sheets/llm-generative-ai/",
        "/interview-prep/cheat-sheets/embeddings-vector-search/",
        "/interview-prep/cheat-sheets/document-ingestion-chunking-indexing/",
        "/interview-prep/cheat-sheets/rag-architecture-retrieval-generation/",
        "/interview-prep/cheat-sheets/rag-evaluation-security-production/",
        "/interview-prep/cheat-sheets/agent-fundamentals-workflow-patterns/",
        "/interview-prep/cheat-sheets/langgraph-deep-dive/",
        "/interview-prep/cheat-sheets/agent-frameworks-libraries-comparison/",
        "/interview-prep/cheat-sheets/agent-protocols-reliability-evaluation/",
        "/interview-prep/cheat-sheets/ai-ml-system-design-production-architecture/",
        "/interview-prep/cheat-sheets/llm-inference-serving-optimization/",
        "/interview-prep/cheat-sheets/mlops-llmops-deployment-lifecycle/",
        "/interview-prep/cheat-sheets/ai-production-monitoring-cost-capacity/",
        "/interview-prep/cheat-sheets/data-distributed-compute-engineering/",
        "/interview-prep/cheat-sheets/ai-security-privacy-governance/",
        "/interview-prep/cheat-sheets/ai-technical-leadership-product-thinking/",
        "/interview-prep/cheat-sheets/project-deep-dive-behavioral-mock-interview/",
        "/interview-prep/cheat-sheets/linear-algebra-calculus-optimization/",
        "/interview-prep/cheat-sheets/experimentation-causal-inference/",
        "/interview-prep/cheat-sheets/data-preparation-eda-feature-engineering/",
        "/interview-prep/cheat-sheets/unsupervised-learning-anomaly-detection/",
        "/interview-prep/cheat-sheets/time-series-forecasting/",
        "/interview-prep/cheat-sheets/recommendation-search-ranking/",
        "/interview-prep/cheat-sheets/unsupervised-learning-dimensionality-reduction/",
        "/interview-prep/cheat-sheets/anomaly-detection-rare-event-modeling/",
        "/interview-prep/cheat-sheets/explainability-fairness-uncertainty-model-governance/",
        "/interview-prep/roles/agentic-ai-engineer/",
        "/interview-prep/roles/data-science-technical-lead/",
        "/interview-prep/roles/senior-data-scientist/",
    )
    for path in required_paths:
        assert path in hub


def test_shared_navigation_exposes_all_learning_sections() -> None:
    home = read(ROOT / "index.html")
    layout = read(ROOT / "_layouts/week.html")
    for content in (home, layout):
        assert 'data-nav-section="roadmap"' in content
        assert 'data-nav-section="interview-prep"' in content
        assert 'data-nav-section="cheat-sheets"' in content
        assert 'data-nav-section="interview-room"' in content
    assert "interview-prep/" in home
    assert "interview-prep/" in layout
    assert "cheat-sheets/" in home
    assert "cheat-sheets/" in layout
    assert "interview-room/" in home
    assert "interview-room/" in layout
    assert "page.back_url" in layout
    assert "page.pagination_url" in layout


def test_interview_room_companion_indexes_the_external_practice_library() -> None:
    page = read(ROOT / "interview-room/index.md")
    assert 'permalink: "/interview-room/"' in page
    assert 'source_repository: "deepankarkotnala/interview_prep"' in page
    assert 'source_commit: "b487032a09e7ae3e0630cf1da660b62a3d988b4a"' in page
    assert "https://deepankarkotnala.github.io/interview_prep/" in page
    for path in (
        "review.html",
        "mock.html",
        "rehearsal.html",
        "rounds.html",
        "tracks.html",
        "visuals.html",
    ):
        assert f"https://deepankarkotnala.github.io/interview_prep/{path}" in page
    assert page.count("https://deepankarkotnala.github.io/interview_prep/topics/") == 21
