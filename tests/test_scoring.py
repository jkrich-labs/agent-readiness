from __future__ import annotations

from agent_readiness.models import CriterionEvaluation
from agent_readiness.scoring import level_from_pass_rate, pass_rate


def test_pass_rate_ignores_skipped() -> None:
    report = {
        "a": CriterionEvaluation(numerator=1, denominator=1, rationale="ok"),
        "b": CriterionEvaluation(numerator=1, denominator=2, rationale="ok"),
        "c": CriterionEvaluation(numerator=None, denominator=2, rationale="skip"),
    }
    assert pass_rate(report) == 0.75


def test_pass_rate_excludes_skipped_criteria() -> None:
    report = {
        "a": CriterionEvaluation(1, 1, "ok"),
        "b": CriterionEvaluation(None, 2, "skip"),
        "c": CriterionEvaluation(0, 1, "fail"),
    }
    assert pass_rate(report) == 0.5


def test_level_thresholds() -> None:
    assert level_from_pass_rate(0.00) == 1
    assert level_from_pass_rate(0.25) == 2
    assert level_from_pass_rate(0.50) == 3
    assert level_from_pass_rate(0.70) == 4
    assert level_from_pass_rate(0.90) == 5
