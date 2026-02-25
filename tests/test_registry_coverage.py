from __future__ import annotations

from agent_readiness.evaluators.registry import build_registry
from agent_readiness.rubric import load_frozen_rubric


def test_registry_has_exact_coverage_for_frozen_rubric() -> None:
    rubric = load_frozen_rubric("v0.62.1")
    registered = set(build_registry(rubric).keys())
    assert registered == set(rubric.criteria_order)
