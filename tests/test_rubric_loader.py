from __future__ import annotations

from agent_readiness.rubric import load_frozen_rubric


def test_rubric_loader_returns_81_unique_criteria() -> None:
    rubric = load_frozen_rubric("v0.62.1")
    assert len(rubric.criteria_order) == 81
    assert len(set(rubric.criteria_order)) == 81


def test_rubric_has_definition_for_every_criterion() -> None:
    rubric = load_frozen_rubric("v0.62.1")
    assert set(rubric.criteria_order) == set(rubric.definitions)
