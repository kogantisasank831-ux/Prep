from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ROLE_BANKS = {
    "AIE": ROOT / "interview-prep/roles/agentic-ai-engineer.md",
    "DSTL": ROOT / "interview-prep/roles/data-science-technical-lead.md",
    "SDS": ROOT / "interview-prep/roles/senior-data-scientist.md",
}

CHEAT_SHEETS = (
    ROOT / "interview-prep/cheat-sheets/python.md",
    ROOT / "interview-prep/cheat-sheets/sql.md",
    ROOT / "interview-prep/cheat-sheets/probability-statistics.md",
    ROOT / "interview-prep/cheat-sheets/machine-learning.md",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_public_pages_have_required_front_matter() -> None:
    pages = (
        ROOT / "interview-prep/index.md",
        ROOT / "interview-prep/master-index.md",
        *CHEAT_SHEETS,
        *ROLE_BANKS.values(),
    )
    permalinks: list[str] = []
    for page in pages:
        content = read(page)
        assert content.startswith("---\n")
        assert 'layout: "week"' in content
        assert 'status: "review"' in content
        match = re.search(r'^permalink: "([^"]+)"$', content, re.MULTILINE)
        assert match is not None, page
        permalinks.append(match.group(1))
    assert len(permalinks) == len(set(permalinks))


def test_role_banks_have_stable_complete_question_contracts() -> None:
    for prefix, path in ROLE_BANKS.items():
        content = read(path)
        ids = re.findall(
            rf"^### ({prefix}-B1-\d{{2}}) — ",
            content,
            re.MULTILINE,
        )
        expected = [f"{prefix}-B1-{index:02d}" for index in range(1, 21)]
        assert ids == expected
        assert len(ids) == len(set(ids)) == 20
        assert content.count("**Strong answer signals**") == 20
        assert content.count("**Follow-up probe:**") == 20
        assert content.count("**Revision links:**") == 20


def test_cheat_sheets_keep_their_rapid_revision_contract() -> None:
    for path in CHEAT_SHEETS:
        content = read(path)
        assert "## 1. Thirty-second revision" in content
        assert content.count("\n# ") == 0


def test_hub_links_every_batch_one_artifact() -> None:
    hub = read(ROOT / "interview-prep/index.md")
    required_paths = (
        "/interview-prep/master-index/",
        "/interview-prep/cheat-sheets/python/",
        "/interview-prep/cheat-sheets/sql/",
        "/interview-prep/cheat-sheets/probability-statistics/",
        "/interview-prep/cheat-sheets/machine-learning/",
        "/interview-prep/roles/agentic-ai-engineer/",
        "/interview-prep/roles/data-science-technical-lead/",
        "/interview-prep/roles/senior-data-scientist/",
    )
    for path in required_paths:
        assert path in hub


def test_shared_navigation_exposes_interview_prep() -> None:
    assert "interview-prep/" in read(ROOT / "index.html")
    layout = read(ROOT / "_layouts/week.html")
    assert "interview-prep/" in layout
    assert "page.back_url" in layout
    assert "page.pagination_url" in layout
