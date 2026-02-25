from __future__ import annotations

import pytest

from agent_readiness.models import AppDescription, CriterionEvaluation, ReadinessReportEnvelope
from agent_readiness.rubric import load_frozen_rubric
from agent_readiness.validator import validate_report_shape


def make_valid_envelope() -> tuple[ReadinessReportEnvelope, object]:
    rubric = load_frozen_rubric("v0.62.1")
    apps = {
        "backend": AppDescription(description="Backend", languages=("python",)),
        "frontend": AppDescription(description="Frontend", languages=("typescript",)),
    }

    report: dict[str, CriterionEvaluation] = {}
    for criterion_id in rubric.criteria_order:
        if criterion_id in rubric.repository_scope:
            report[criterion_id] = CriterionEvaluation(numerator=1, denominator=1, rationale="ok")
        else:
            report[criterion_id] = CriterionEvaluation(numerator=2, denominator=2, rationale="ok")

    envelope = ReadinessReportEnvelope(
        repoUrl="https://example.com/repo.git",
        rubricVersion=rubric.version,
        apps=apps,
        report=report,
    )
    return envelope, rubric


def test_validator_rejects_missing_criterion_key() -> None:
    envelope, rubric = make_valid_envelope()
    envelope.report.pop("lint_config")
    with pytest.raises(ValueError):
        validate_report_shape(envelope, rubric)


def test_validator_rejects_non_skippable_null_numerator() -> None:
    envelope, rubric = make_valid_envelope()
    envelope.report["lint_config"] = CriterionEvaluation(numerator=None, denominator=2, rationale="invalid")
    with pytest.raises(ValueError):
        validate_report_shape(envelope, rubric)
