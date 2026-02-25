from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from ..command_runner import CommandResult, run_command
from ..discovery import RepositoryDiscovery
from ..models import CriterionEvaluation
from ..rubric import FrozenRubric


class CriterionEvaluator(Protocol):
    def evaluate(self, ctx: "EvaluationContext") -> CriterionEvaluation:
        ...


@dataclass
class EvaluationContext:
    repo_root: Path
    discovery: RepositoryDiscovery
    rubric: FrozenRubric
    execute_commands: bool = True
    command_timeout: int = 20
    cache: dict[str, object] = field(default_factory=dict)
    _file_index: tuple[str, ...] = field(default_factory=tuple, init=False, repr=False)

    def __post_init__(self) -> None:
        self.repo_root = self.repo_root.resolve()
        self._file_index = self._build_file_index()

    @property
    def app_count(self) -> int:
        return len(self.discovery.apps)

    def app_dir(self, app_path: str) -> Path:
        return self.repo_root if app_path == "." else self.repo_root / app_path

    def has_any_paths(self, paths: tuple[str, ...], within: Path | None = None) -> bool:
        base = within or self.repo_root
        return any((base / rel).exists() for rel in paths)

    def glob_exists(self, pattern: str, within: Path | None = None) -> bool:
        base = within or self.repo_root
        return any(base.glob(pattern))

    def text_search(self, tokens: tuple[str, ...], within: Path | None = None) -> bool:
        """Search file paths and file contents for tokens.

        First checks file paths in the index (fast). If no match, reads
        file contents of relevant files (slower but more thorough).
        """
        base = within.resolve() if within else self.repo_root
        prefix = "" if base == self.repo_root else str(base.relative_to(self.repo_root)).rstrip("/") + "/"
        lowered_tokens = tuple(token.lower() for token in tokens)

        # Phase 1: search file paths (fast)
        for rel in self._file_index:
            if prefix and not rel.startswith(prefix):
                continue
            if all(token in rel for token in lowered_tokens):
                return True

        # Phase 2: search file contents
        # Only read text-like files to avoid binary reads
        _text_suffixes = {
            ".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs",
            ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".conf",
            ".md", ".txt", ".rst", ".html", ".css", ".scss",
            ".go", ".rs", ".java", ".rb", ".sh", ".bash", ".zsh",
            ".xml", ".env", ".properties", ".graphql", ".gql",
            ".dockerfile", ".tf", ".hcl",
        }
        files_checked = 0
        max_content_files = 500
        for rel in self._file_index:
            if prefix and not rel.startswith(prefix):
                continue
            suffix = "." + rel.rsplit(".", 1)[-1] if "." in rel else ""
            # Also read known config files without extensions or with special names
            basename = rel.rsplit("/", 1)[-1] if "/" in rel else rel
            if suffix not in _text_suffixes and basename not in (
                "dockerfile", "makefile", "gemfile", "rakefile",
                ".gitignore", ".dockerignore", ".env.example",
            ):
                continue
            files_checked += 1
            if files_checked > max_content_files:
                break
            filepath = self.repo_root / rel
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            if all(token in content for token in lowered_tokens):
                return True

        return False

    def run(self, command: list[str], cwd: Path | None = None, timeout: int | None = None) -> CommandResult:
        if not self.execute_commands:
            return CommandResult(
                command=tuple(command),
                cwd=str((cwd or self.repo_root).resolve()),
                exit_code=127,
                stdout="",
                stderr="command execution disabled",
                duration_ms=0,
                timed_out=False,
            )
        return run_command(command=command, cwd=cwd or self.repo_root, timeout=timeout or self.command_timeout)

    def _build_file_index(self, max_files: int = 12000) -> tuple[str, ...]:
        files: list[str] = []
        skip_dirs = {".git", "node_modules", ".venv", "dist", "build", "target", "coverage", ".pytest_cache"}
        for path in self.repo_root.rglob("*"):
            if any(part in skip_dirs for part in path.parts):
                continue
            if not path.is_file():
                continue
            files.append(str(path.relative_to(self.repo_root)).lower())
            if len(files) >= max_files:
                break
        files.sort()
        return tuple(files)


def repo_score(passed: bool, rationale: str, evidence: tuple[str, ...] = ()) -> CriterionEvaluation:
    return CriterionEvaluation(
        numerator=int(passed),
        denominator=1,
        rationale=rationale,
        evidence=evidence,
    )


def skip_repo(rationale: str, evidence: tuple[str, ...] = ()) -> CriterionEvaluation:
    return CriterionEvaluation(
        numerator=None,
        denominator=1,
        rationale=rationale,
        evidence=evidence,
    )


def app_score(numerator: int, denominator: int, rationale: str, evidence: tuple[str, ...] = ()) -> CriterionEvaluation:
    return CriterionEvaluation(
        numerator=numerator,
        denominator=denominator,
        rationale=rationale,
        evidence=evidence,
    )


def skip_app(denominator: int, rationale: str, evidence: tuple[str, ...] = ()) -> CriterionEvaluation:
    return CriterionEvaluation(
        numerator=None,
        denominator=denominator,
        rationale=rationale,
        evidence=evidence,
    )
