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

ALL_CHEAT_SHEETS = (
    BATCH_ONE_CHEAT_SHEETS
    + BATCH_TWO_CHEAT_SHEETS
    + BATCH_THREE_CHEAT_SHEETS
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def page_status(content: str) -> str:
    match = re.search(r'^status: "([^"]+)"$', content, re.MULTILINE)
    assert match is not None
    return match.group(1)


def test_public_pages_have_required_front_matter() -> None:
    approved_pages = (
        ROOT / "interview-prep/master-index.md",
        ROOT / "interview-prep/index.md",
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


def test_role_banks_have_two_stable_complete_batches() -> None:
    for prefix, path in ROLE_BANKS.items():
        content = read(path)
        for batch in (1, 2, 3):
            ids = re.findall(
                rf"^### ({prefix}-B{batch}-\d{{2}}) — ",
                content,
                re.MULTILINE,
            )
            expected = [
                f"{prefix}-B{batch}-{index:02d}"
                for index in range(1, 21)
            ]
            assert ids == expected
            assert len(ids) == len(set(ids)) == 20
        assert content.count("**Strong answer signals**") == 60
        assert content.count("**Follow-up probe:**") == 60
        assert content.count("**Revision links:**") == 60
        assert "question_count: 60" in content


def test_cheat_sheets_keep_their_rapid_revision_contract() -> None:
    for path in ALL_CHEAT_SHEETS:
        content = read(path)
        assert "## 1. Thirty-second revision" in content
        assert content.count("\n# ") == 0


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
        "/interview-prep/roles/agentic-ai-engineer/",
        "/interview-prep/roles/data-science-technical-lead/",
        "/interview-prep/roles/senior-data-scientist/",
    )
    for path in required_paths:
        assert path in hub


def test_shared_navigation_exposes_interview_prep() -> None:
    home = read(ROOT / "index.html")
    layout = read(ROOT / "_layouts/week.html")
    for content in (home, layout):
        assert 'data-nav-section="roadmap"' in content
        assert 'data-nav-section="interview-prep"' in content
    assert "interview-prep/" in home
    assert "interview-prep/" in layout
    assert "page.back_url" in layout
    assert "page.pagination_url" in layout
