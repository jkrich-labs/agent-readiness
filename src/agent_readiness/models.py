from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class AppDescription:
    description: str
    languages: tuple[str, ...] = ()


@dataclass(frozen=True)
class CriterionEvaluation:
    numerator: Optional[int]
    denominator: int
    rationale: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelUsed:
    id: str
    reasoningEffort: str


@dataclass(frozen=True)
class ReadinessReportEnvelope:
    repoUrl: str
    report: dict[str, CriterionEvaluation]
    apps: dict[str, AppDescription]
    rubricVersion: str
    branch: Optional[str] = None
    commitHash: Optional[str] = None
    hasLocalChanges: Optional[bool] = None
    hasNonRemoteCommits: Optional[bool] = None
    modelUsed: Optional[ModelUsed] = None
    droidVersion: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)
