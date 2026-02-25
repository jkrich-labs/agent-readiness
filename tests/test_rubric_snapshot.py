from __future__ import annotations

from pathlib import Path


def test_frozen_rubric_has_exactly_81_criteria() -> None:
    lines = (
        Path("rubric/droid/v0.62.1/criteria_order.txt")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    assert len(lines) == 81


def test_frozen_rubric_scope_counts_match_expected() -> None:
    import json

    scope = json.loads(Path("rubric/droid/v0.62.1/criteria_scope.json").read_text())
    assert len(scope["repository_scope"]) == 43
    assert len(scope["application_scope"]) == 38
