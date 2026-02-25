from __future__ import annotations

from .rubric import DEFAULT_RUBRIC_VERSION, load_frozen_rubric


def _load_default() -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    rubric = load_frozen_rubric(DEFAULT_RUBRIC_VERSION)
    repo_scope = tuple(c for c in rubric.criteria_order if c in rubric.repository_scope)
    app_scope = tuple(c for c in rubric.criteria_order if c in rubric.application_scope)
    return repo_scope, app_scope, tuple(rubric.criteria_order)


REPOSITORY_SCOPE_CRITERIA, APPLICATION_SCOPE_CRITERIA, ALL_CRITERIA = _load_default()

EXPECTED_REPOSITORY_SCOPE_COUNT = 43
EXPECTED_APPLICATION_SCOPE_COUNT = 38
EXPECTED_TOTAL_COUNT = 81


def validate_criteria_inventory() -> None:
    if len(REPOSITORY_SCOPE_CRITERIA) != EXPECTED_REPOSITORY_SCOPE_COUNT:
        raise ValueError("Repository scope criteria count mismatch")
    if len(APPLICATION_SCOPE_CRITERIA) != EXPECTED_APPLICATION_SCOPE_COUNT:
        raise ValueError("Application scope criteria count mismatch")
    if len(ALL_CRITERIA) != EXPECTED_TOTAL_COUNT:
        raise ValueError("Total criteria count mismatch")
    if len(set(ALL_CRITERIA)) != EXPECTED_TOTAL_COUNT:
        raise ValueError("Criteria IDs must be unique")
