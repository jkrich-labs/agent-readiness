from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .discovery import discover_repository
from .evaluators import EvaluationContext, build_registry
from .models import AppDescription, CriterionEvaluation, ReadinessReportEnvelope
from .rubric import DEFAULT_RUBRIC_VERSION, FrozenRubric, load_frozen_rubric
from .scoring import level_from_pass_rate, pass_rate
from .validator import validate_report_shape


@dataclass(frozen=True)
class RunOptions:
    execute_commands: bool = True
    command_timeout: int = 20


class ReadinessRunner:
    def __init__(
        self,
        repo_path: Path,
        repo_url: str | None = None,
        rubric_version: str = DEFAULT_RUBRIC_VERSION,
        options: RunOptions | None = None,
    ) -> None:
        self.repo_path = repo_path.resolve()
        self.rubric: FrozenRubric = load_frozen_rubric(rubric_version)
        self.options = options or RunOptions()
        self.repo_url = repo_url or self._detect_repo_url()

    def evaluate(self) -> ReadinessReportEnvelope:
        discovery = discover_repository(self.repo_path)
        apps = {
            path: AppDescription(description=app.description, languages=app.languages)
            for path, app in discovery.apps.items()
        }

        ctx = EvaluationContext(
            repo_root=self.repo_path,
            discovery=discovery,
            rubric=self.rubric,
            execute_commands=self.options.execute_commands,
            command_timeout=self.options.command_timeout,
        )

        registry = build_registry(self.rubric)

        report: dict[str, CriterionEvaluation] = {}
        for criterion_id in self.rubric.criteria_order:
            evaluator = registry[criterion_id]
            try:
                report[criterion_id] = evaluator.evaluate(ctx)
            except Exception as exc:  # pragma: no cover - defensive path
                denominator = 1 if criterion_id in self.rubric.repository_scope else len(apps)
                report[criterion_id] = CriterionEvaluation(
                    numerator=0,
                    denominator=denominator,
                    rationale=f"Evaluation failed: {exc}",
                    evidence=(f"exception:{type(exc).__name__}",),
                )

        envelope = ReadinessReportEnvelope(
            repoUrl=self.repo_url,
            report=report,
            apps=apps,
            rubricVersion=self.rubric.version,
            branch=self._git("rev-parse", "--abbrev-ref", "HEAD"),
            commitHash=self._git("rev-parse", "HEAD"),
            hasLocalChanges=self._git("status", "--porcelain") not in (None, ""),
            hasNonRemoteCommits=self._has_non_remote_commits(),
        )

        validate_report_shape(envelope, self.rubric)
        return envelope

    @staticmethod
    def summarize(envelope: ReadinessReportEnvelope) -> tuple[float, int]:
        rate = pass_rate(envelope.report)
        level = level_from_pass_rate(rate)
        return rate, level

    def _git(self, *args: str) -> str | None:
        from .command_runner import run_command

        result = run_command(["git", *args], cwd=self.repo_path, timeout=6)
        if result.exit_code != 0:
            return None
        return result.stdout.strip()

    def _has_non_remote_commits(self) -> bool | None:
        from .command_runner import run_command

        head = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.repo_path, timeout=6)
        if head.exit_code != 0:
            return None
        branch = head.stdout.strip()
        cmp_result = run_command(
            ["git", "rev-list", "--count", f"origin/{branch}..HEAD"],
            cwd=self.repo_path,
            timeout=6,
        )
        if cmp_result.exit_code != 0:
            return None
        try:
            return int(cmp_result.stdout.strip() or "0") > 0
        except ValueError:
            return None

    def _detect_repo_url(self) -> str:
        remote = self._git("remote", "get-url", "origin")
        if remote:
            return remote
        return f"file://{self.repo_path}"
