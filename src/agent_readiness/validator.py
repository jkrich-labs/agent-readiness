from __future__ import annotations

from .models import ReadinessReportEnvelope
from .rubric import FrozenRubric


def validate_report_shape(envelope: ReadinessReportEnvelope, rubric: FrozenRubric) -> None:
    report_keys = set(envelope.report.keys())
    expected_keys = set(rubric.criteria_order)

    missing = expected_keys - report_keys
    extra = report_keys - expected_keys
    if missing or extra:
        raise ValueError(f"Report keys mismatch. missing={sorted(missing)} extra={sorted(extra)}")

    app_count = len(envelope.apps)
    if app_count < 1:
        raise ValueError("apps is required and must have at least one app")

    for criterion in rubric.repository_scope:
        if envelope.report[criterion].denominator != 1:
            raise ValueError(f"{criterion} must have denominator=1")

    for criterion in rubric.application_scope:
        if envelope.report[criterion].denominator != app_count:
            raise ValueError(f"{criterion} must have denominator={app_count}")

    for criterion_id, evaluation in envelope.report.items():
        if evaluation.denominator < 1:
            raise ValueError(f"{criterion_id} denominator must be >=1")

        if not evaluation.rationale or len(evaluation.rationale) > 500:
            raise ValueError(f"{criterion_id} rationale must be non-empty and <= 500 chars")

        if evaluation.numerator is None:
            if not rubric.definitions[criterion_id].skippable:
                raise ValueError(f"{criterion_id} is not skippable and cannot have numerator=null")
            continue

        if evaluation.numerator < 0 or evaluation.numerator > evaluation.denominator:
            raise ValueError(f"{criterion_id} numerator must be in [0, denominator] or null")
