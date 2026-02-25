from __future__ import annotations

from .models import CriterionEvaluation


def pass_rate(report: dict[str, CriterionEvaluation]) -> float:
    non_skipped = [value for value in report.values() if value.numerator is not None]
    if not non_skipped:
        return 0.0

    ratios = [value.numerator / value.denominator for value in non_skipped if value.numerator is not None]
    return sum(ratios) / len(ratios)


def level_from_pass_rate(rate: float) -> int:
    if rate < 0:
        return 1
    if rate < 0.2:
        return 1
    if rate < 0.4:
        return 2
    if rate < 0.6:
        return 3
    if rate < 0.8:
        return 4
    return 5
