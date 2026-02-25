from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_RUBRIC_VERSION = "v0.62.1"
EXPECTED_REPOSITORY_SCOPE_COUNT = 43
EXPECTED_APPLICATION_SCOPE_COUNT = 38
EXPECTED_TOTAL_COUNT = 81


@dataclass(frozen=True)
class CriterionDefinition:
    id: str
    scope: str
    level: int
    skippable: bool
    description: str


@dataclass(frozen=True)
class FrozenRubric:
    version: str
    criteria_order: tuple[str, ...]
    repository_scope: frozenset[str]
    application_scope: frozenset[str]
    definitions: dict[str, CriterionDefinition]
    scoring_rules: dict[str, object]
    provenance: dict[str, object]

    def scope_for(self, criterion_id: str) -> str:
        if criterion_id in self.repository_scope:
            return "repository"
        if criterion_id in self.application_scope:
            return "application"
        raise KeyError(f"Unknown criterion id: {criterion_id}")


def _default_rubric_root() -> Path:
    return Path(__file__).resolve().parents[2] / "rubric" / "droid"


def load_frozen_rubric(version: str = DEFAULT_RUBRIC_VERSION, rubric_root: Path | None = None) -> FrozenRubric:
    base = (rubric_root or _default_rubric_root()) / version
    criteria_order_path = base / "criteria_order.txt"
    criteria_scope_path = base / "criteria_scope.json"
    scoring_rules_path = base / "scoring_rules.json"
    provenance_path = base / "provenance.json"

    criteria_order = tuple(
        line.strip()
        for line in criteria_order_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )

    scope_data = json.loads(criteria_scope_path.read_text(encoding="utf-8"))
    scoring_rules = json.loads(scoring_rules_path.read_text(encoding="utf-8"))
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))

    repo_scope = tuple(scope_data["repository_scope"])
    app_scope = tuple(scope_data["application_scope"])

    if len(repo_scope) != EXPECTED_REPOSITORY_SCOPE_COUNT:
        raise ValueError(f"Repository scope must contain {EXPECTED_REPOSITORY_SCOPE_COUNT} criteria")
    if len(app_scope) != EXPECTED_APPLICATION_SCOPE_COUNT:
        raise ValueError(f"Application scope must contain {EXPECTED_APPLICATION_SCOPE_COUNT} criteria")
    if len(criteria_order) != EXPECTED_TOTAL_COUNT:
        raise ValueError(f"Rubric must contain {EXPECTED_TOTAL_COUNT} criteria")
    if len(set(criteria_order)) != EXPECTED_TOTAL_COUNT:
        raise ValueError("Rubric criteria IDs must be unique")

    expected = list(repo_scope) + list(app_scope)
    if list(criteria_order) != expected:
        raise ValueError("criteria_order.txt must match repository_scope + application_scope order")

    definitions: dict[str, CriterionDefinition] = {}
    for criterion_id, raw in scope_data["criteria"].items():
        definitions[criterion_id] = CriterionDefinition(
            id=criterion_id,
            scope=raw["scope"],
            level=int(raw["level"]),
            skippable=bool(raw["skippable"]),
            description=str(raw["description"]),
        )

    if set(definitions) != set(criteria_order):
        raise ValueError("criteria definitions must match criteria_order exactly")

    return FrozenRubric(
        version=version,
        criteria_order=criteria_order,
        repository_scope=frozenset(repo_scope),
        application_scope=frozenset(app_scope),
        definitions=definitions,
        scoring_rules=scoring_rules,
        provenance=provenance,
    )
