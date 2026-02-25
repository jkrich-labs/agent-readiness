from __future__ import annotations

import json
from pathlib import Path

_RUBRIC_DIR = Path(__file__).resolve().parent.parent / "rubric" / "droid" / "v0.62.1"


def test_frozen_rubric_has_exactly_81_criteria() -> None:
    lines = (_RUBRIC_DIR / "criteria_order.txt").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 81


def test_frozen_rubric_scope_counts_match_expected() -> None:
    scope = json.loads((_RUBRIC_DIR / "criteria_scope.json").read_text())
    assert len(scope["repository_scope"]) == 43
    assert len(scope["application_scope"]) == 38
