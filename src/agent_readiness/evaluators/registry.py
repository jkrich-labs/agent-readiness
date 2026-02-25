from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from ..models import CriterionEvaluation
from ..rubric import DEFAULT_RUBRIC_VERSION, FrozenRubric, load_frozen_rubric
from .base import EvaluationContext, app_score, repo_score, skip_app, skip_repo


@dataclass(frozen=True)
class _FunctionEvaluator:
    criterion_id: str

    def evaluate(self, ctx: EvaluationContext) -> CriterionEvaluation:
        return _evaluate_criterion(ctx, self.criterion_id)


def build_registry(rubric: FrozenRubric | None = None) -> dict[str, _FunctionEvaluator]:
    resolved = rubric or load_frozen_rubric(DEFAULT_RUBRIC_VERSION)
    registry = {criterion_id: _FunctionEvaluator(criterion_id=criterion_id) for criterion_id in resolved.criteria_order}
    if set(registry) != set(resolved.criteria_order):
        raise ValueError("Registry does not match frozen rubric coverage")
    return registry


def _evaluate_criterion(ctx: EvaluationContext, criterion_id: str) -> CriterionEvaluation:
    definition = ctx.rubric.definitions[criterion_id]
    if definition.scope == "repository":
        return _evaluate_repository_criterion(ctx, criterion_id)
    return _evaluate_application_criterion(ctx, criterion_id)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(token.lower() in lowered for token in tokens)


_UNSET = object()


def _git_remote_slug(ctx: EvaluationContext) -> str | None:
    key = "git_remote_slug"
    cached = ctx.cache.get(key, _UNSET)
    if cached is not _UNSET:
        return cached  # type: ignore[return-value]

    result = ctx.run(["git", "remote", "get-url", "origin"], timeout=5)
    if result.exit_code != 0:
        ctx.cache[key] = None
        return None

    remote = result.stdout.strip()
    match = re.search(r"github\.com[:/]([^/]+/[^/.]+)(?:\.git)?$", remote)
    if not match:
        ctx.cache[key] = None
        return None

    slug = match.group(1)
    ctx.cache[key] = slug
    return slug


def _gh_auth_ok(ctx: EvaluationContext) -> bool:
    key = "gh_auth_ok"
    cached = ctx.cache.get(key)
    if isinstance(cached, bool):
        return cached

    version = ctx.run(["gh", "--version"], timeout=5)
    if version.exit_code != 0:
        ctx.cache[key] = False
        return False

    auth = ctx.run(["gh", "auth", "status"], timeout=8)
    ok = auth.exit_code == 0
    ctx.cache[key] = ok
    return ok


def _criterion_skippable(ctx: EvaluationContext, criterion_id: str) -> bool:
    return ctx.rubric.definitions[criterion_id].skippable


def _evaluate_repository_criterion(ctx: EvaluationContext, criterion_id: str) -> CriterionEvaluation:
    root = ctx.repo_root
    workflows = root / ".github" / "workflows"
    readme_text = _read_text(root / "README.md") + "\n" + _read_text(root / "AGENTS.md")

    if criterion_id == "large_file_detection":
        passed = ctx.has_any_paths((".gitattributes", ".pre-commit-config.yaml", ".github/workflows"))
        passed = passed or ctx.text_search(("large", "file"))
        return repo_score(passed, "Large-file guardrails detected" if passed else "No large-file detection tooling found")

    if criterion_id == "tech_debt_tracking":
        passed = ctx.has_any_paths(("sonar-project.properties", ".pre-commit-config.yaml"))
        passed = passed or _contains_any(readme_text, ("todo", "tech debt", "debt"))
        return repo_score(passed, "Tech-debt tracking evidence found" if passed else "No explicit tech-debt tracking evidence found")

    if criterion_id == "build_cmd_doc":
        passed = _contains_any(readme_text, ("npm run build", "python -m", "uv run", "make build", "cargo build", "go build"))
        return repo_score(passed, "Build commands are documented" if passed else "Build commands are not documented")

    if criterion_id == "deps_pinned":
        lockfiles = (
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "poetry.lock",
            "uv.lock",
            "Pipfile.lock",
            "Cargo.lock",
            "go.sum",
        )
        passed = any((root / lock).exists() for lock in lockfiles)
        return repo_score(passed, "Dependency lockfiles detected" if passed else "No dependency lockfile found")

    if criterion_id == "vcs_cli_tools":
        ok = _gh_auth_ok(ctx)
        return repo_score(ok, "GitHub CLI is installed and authenticated" if ok else "GitHub CLI not authenticated")

    if criterion_id == "automated_pr_review":
        if not _gh_auth_ok(ctx):
            return skip_repo("Skipping: GitHub CLI is not authenticated")
        passed = ctx.text_search(("danger",)) or ctx.text_search(("pull_request_review",))
        if workflows.exists():
            for file in workflows.glob("*.y*ml"):
                if _contains_any(_read_text(file), ("reviewdog", "droid", "pull_request_review", "comment on pr", "code review")):
                    passed = True
                    break
        return repo_score(passed, "Automated PR review workflow found" if passed else "No automated PR review workflow found")

    if criterion_id == "agentic_development":
        has_agent_dirs = ctx.has_any_paths((".claude", ".codex", ".factory", ".agents"))
        git_log = ctx.run(["git", "log", "--format=%an|||%ae|||%s|||%b", "-50"], timeout=8)
        has_agent_authorship = _contains_any(git_log.stdout, ("claude", "codex", "factory-droid", "bot]"))
        passed = has_agent_dirs or has_agent_authorship
        return repo_score(passed, "Agent workflow evidence detected" if passed else "No clear agentic-development evidence found")

    if criterion_id == "fast_ci_feedback":
        if not _gh_auth_ok(ctx):
            return skip_repo("Skipping: GitHub CLI is not authenticated")
        result = ctx.run(["gh", "pr", "list", "--state", "merged", "--limit", "5", "--json", "statusCheckRollup"], timeout=15)
        if result.exit_code != 0:
            return skip_repo("Skipping: Unable to query PR status checks")
        # Conservative: evidence of CI exists, but duration parsing can be noisy across providers.
        has_checks = "statusCheckRollup" in result.stdout
        return repo_score(has_checks, "CI status checks detected for merged PRs" if has_checks else "No CI timing evidence found")

    if criterion_id == "build_performance_tracking":
        if not _gh_auth_ok(ctx) and not workflows.exists():
            return skip_repo("Skipping: CI metadata unavailable")
        passed = ctx.text_search(("cache", "build")) or ctx.text_search(("turbo", "nx"))
        return repo_score(passed, "Build performance/caching evidence found" if passed else "No build performance tracking evidence found")

    if criterion_id == "deployment_frequency":
        if not _gh_auth_ok(ctx):
            return skip_repo("Skipping: GitHub CLI is not authenticated")
        releases = ctx.run(["gh", "release", "list", "--limit", "10"], timeout=10)
        runs = ctx.run(["gh", "run", "list", "--limit", "20"], timeout=10)
        passed = releases.exit_code == 0 and bool(releases.stdout.strip())
        passed = passed or (runs.exit_code == 0 and _contains_any(runs.stdout, ("deploy", "release")))
        return repo_score(passed, "Recent deployment automation activity detected" if passed else "No frequent deployment evidence found")

    if criterion_id == "single_command_setup":
        passed = _contains_any(readme_text, ("docker compose up", "make dev", "npm run dev", "uv sync", "cargo run"))
        return repo_score(passed, "Single-command setup is documented" if passed else "Single-command setup is not documented")

    if criterion_id == "feature_flag_infrastructure":
        passed = ctx.text_search(("launchdarkly",)) or ctx.text_search(("growthbook",)) or ctx.text_search(("unleash",))
        passed = passed or ctx.text_search(("feature flag",))
        return repo_score(passed, "Feature flag infrastructure detected" if passed else "No feature flag infrastructure detected")

    if criterion_id == "release_notes_automation":
        passed = ctx.text_search(("changeset",)) or ctx.text_search(("semantic-release",))
        passed = passed or ctx.text_search(("release notes",))
        return repo_score(passed, "Release-notes automation detected" if passed else "No release-notes automation detected")

    if criterion_id == "progressive_rollout":
        has_infra = ctx.has_any_paths(("k8s", "helm", "terraform", "argocd"))
        if not has_infra:
            return skip_repo("Skipping: not an infra deployment repository")
        passed = ctx.text_search(("canary",)) or ctx.text_search(("rollout", "percentage"))
        return repo_score(passed, "Progressive rollout configuration found" if passed else "No progressive rollout evidence found")

    if criterion_id == "rollback_automation":
        has_infra = ctx.has_any_paths(("k8s", "helm", "terraform", "argocd"))
        if not has_infra:
            return skip_repo("Skipping: not an infra deployment repository")
        passed = ctx.text_search(("rollback",))
        return repo_score(passed, "Rollback automation/documentation detected" if passed else "No rollback automation evidence found")

    if criterion_id == "monorepo_tooling":
        if ctx.app_count <= 1:
            return skip_repo("Skipping: single-application repository")
        passed = ctx.has_any_paths(("pnpm-workspace.yaml", "nx.json", "turbo.json", "go.work", "WORKSPACE"))
        passed = passed or ctx.text_search(("workspaces",))
        return repo_score(passed, "Monorepo tooling detected" if passed else "No monorepo tooling detected")

    if criterion_id == "version_drift_detection":
        if ctx.app_count <= 1:
            return skip_repo("Skipping: single-application repository")
        passed = ctx.text_search(("syncpack",)) or ctx.text_search(("manypkg",))
        passed = passed or ctx.text_search(("dependabot", "group"))
        return repo_score(passed, "Version-drift detection tooling found" if passed else "No version-drift detection tooling found")

    if criterion_id == "release_automation":
        passed = False
        if workflows.exists():
            for file in workflows.glob("*.y*ml"):
                content = _read_text(file)
                if _contains_any(content, ("release", "deploy", "publish", "workflow_dispatch")):
                    passed = True
                    break
        return repo_score(passed, "Release automation workflow found" if passed else "No release automation workflow found")

    if criterion_id == "dead_feature_flag_detection":
        feature_flag_result = _evaluate_repository_criterion(ctx, "feature_flag_infrastructure")
        if feature_flag_result.numerator == 0:
            return skip_repo("Skipping: feature-flag infrastructure not detected")
        passed = ctx.text_search(("stale flag",)) or ctx.text_search(("dead flag",))
        return repo_score(passed, "Dead feature-flag detection found" if passed else "No dead feature-flag detection found")

    if criterion_id == "agents_md":
        path = root / "AGENTS.md"
        passed = path.exists() and len(_read_text(path).strip()) > 100
        return repo_score(passed, "AGENTS.md exists and is non-trivial" if passed else "AGENTS.md missing or too short")

    if criterion_id == "readme":
        path = root / "README.md"
        passed = path.exists() and len(_read_text(path).strip()) > 100
        return repo_score(passed, "README.md exists and is non-trivial" if passed else "README.md missing or too short")

    if criterion_id == "automated_doc_generation":
        passed = ctx.text_search(("openapi", "generate")) or ctx.text_search(("sphinx", "build"))
        passed = passed or ctx.text_search(("typedoc",)) or ctx.text_search(("docs", "workflow"))
        return repo_score(passed, "Automated documentation tooling found" if passed else "No automated documentation tooling found")

    if criterion_id == "skills":
        skills_dirs = (root / ".claude" / "skills", root / ".factory" / "skills", root / ".skills")
        valid = False
        for base in skills_dirs:
            if not base.is_dir():
                continue
            for skill_file in base.glob("*/SKILL.md"):
                text = _read_text(skill_file)
                if _contains_any(text, ("name:", "description:")):
                    valid = True
                    break
            if valid:
                break
        return repo_score(valid, "Valid skill definition(s) found" if valid else "No valid skills detected")

    if criterion_id == "documentation_freshness":
        result = ctx.run(["git", "log", "--since=180 days ago", "--name-only", "--", "README.md", "AGENTS.md", "CONTRIBUTING.md"], timeout=10)
        passed = result.exit_code == 0 and bool(result.stdout.strip())
        return repo_score(passed, "Key docs updated in the last 180 days" if passed else "No recent key-doc updates found")

    if criterion_id == "service_flow_documented":
        passed = ctx.text_search(("architecture", "diagram"))
        passed = passed or ctx.glob_exists("docs/**/architecture*")
        passed = passed or ctx.glob_exists("docs/**/diagrams*")
        passed = passed or ctx.glob_exists("**/*.mermaid") or ctx.glob_exists("**/*.puml")
        return repo_score(passed, "Service flow documentation found" if passed else "No service flow documentation found")

    if criterion_id == "agents_md_validation":
        passed = ctx.text_search(("agents.md", "check")) or ctx.text_search(("validate", "agents"))
        return repo_score(passed, "AGENTS.md validation automation found" if passed else "No AGENTS.md validation automation found")

    if criterion_id == "devcontainer":
        passed = (root / ".devcontainer" / "devcontainer.json").exists()
        return repo_score(passed, "Devcontainer configuration found" if passed else "No devcontainer configuration found")

    if criterion_id == "env_template":
        passed = (root / ".env.example").exists() or _contains_any(readme_text, ("environment variables", "env var", ".env"))
        return repo_score(passed, "Environment template/documentation found" if passed else "No environment template/documentation found")

    if criterion_id == "local_services_setup":
        if ctx.has_any_paths(("docker-compose.yml", "compose.yml", "docker-compose.yaml")):
            return repo_score(True, "Local services setup found via compose file")
        return skip_repo("Skipping: no external local services detected")

    if criterion_id == "devcontainer_runnable":
        if not (root / ".devcontainer" / "devcontainer.json").exists():
            return skip_repo("Skipping: no devcontainer configuration")
        probe = ctx.run(["devcontainer", "--version"], timeout=5)
        if probe.exit_code != 0:
            return skip_repo("Skipping: devcontainer CLI not available")
        return repo_score(True, "Devcontainer CLI is available")

    if criterion_id == "runbooks_documented":
        passed = ctx.text_search(("runbook",)) or ctx.glob_exists("docs/**/ops*") or ctx.glob_exists("docs/**/troubleshooting*")
        return repo_score(passed, "Runbook documentation found" if passed else "No runbook documentation found")

    if criterion_id == "branch_protection":
        if not _gh_auth_ok(ctx):
            return skip_repo("Skipping: GitHub CLI is not authenticated")
        slug = _git_remote_slug(ctx)
        if not slug:
            return skip_repo("Skipping: unable to determine repository slug")
        rulesets = ctx.run(["gh", "api", f"repos/{slug}/rulesets"], timeout=10)
        passed = rulesets.exit_code == 0 and rulesets.stdout.strip() not in ("[]", "")
        if not passed:
            legacy = ctx.run(["gh", "api", f"repos/{slug}/branches/main/protection"], timeout=10)
            passed = legacy.exit_code == 0
        return repo_score(passed, "Branch protection/rulesets detected" if passed else "No branch protection detected")

    if criterion_id == "secret_scanning":
        if not _gh_auth_ok(ctx):
            return skip_repo("Skipping: GitHub CLI is not authenticated")
        slug = _git_remote_slug(ctx)
        if not slug:
            return skip_repo("Skipping: unable to determine repository slug")
        check = ctx.run(["gh", "api", f"repos/{slug}/secret-scanning/alerts", "--paginate"], timeout=12)
        passed = check.exit_code == 0
        return repo_score(passed, "Secret scanning is enabled" if passed else "Secret scanning not enabled or inaccessible")

    if criterion_id == "codeowners":
        passed = (root / "CODEOWNERS").exists() or (root / ".github" / "CODEOWNERS").exists()
        return repo_score(passed, "CODEOWNERS file found" if passed else "CODEOWNERS file not found")

    if criterion_id == "automated_security_review":
        if not _gh_auth_ok(ctx):
            return skip_repo("Skipping: GitHub CLI is not authenticated")
        slug = _git_remote_slug(ctx)
        if not slug:
            return skip_repo("Skipping: unable to determine repository slug")
        scans = ctx.run(["gh", "api", f"repos/{slug}/code-scanning/analyses"], timeout=12)
        passed = scans.exit_code == 0
        return repo_score(passed, "Automated code scanning detected" if passed else "No automated code scanning detected")

    if criterion_id == "dependency_update_automation":
        passed = (root / ".github" / "dependabot.yml").exists() or (root / "renovate.json").exists()
        return repo_score(passed, "Dependency update automation configured" if passed else "No dependency update automation configured")

    if criterion_id == "gitignore_comprehensive":
        text = _read_text(root / ".gitignore")
        if not text.strip():
            return repo_score(False, ".gitignore is missing or empty")
        # Always require .env (secrets); other tokens depend on detected languages
        required = [".env"]
        languages = ctx.discovery.languages
        if any(lang in languages for lang in ("typescript", "javascript")):
            required.append("node_modules")
        if "python" in languages:
            required.append(".venv")
        # At least one build output pattern
        has_build_output = any(token in text for token in ("dist", "build", "target", "__pycache__"))
        passed = all(token in text for token in required) and has_build_output
        return repo_score(passed, "gitignore covers common generated/secrets files" if passed else "gitignore missing common exclusions")

    if criterion_id == "privacy_compliance":
        passed = ctx.text_search(("gdpr",)) or ctx.text_search(("privacy", "policy"))
        return repo_score(passed, "Privacy compliance documentation/tooling found" if passed else "No privacy compliance evidence found")

    if criterion_id == "secrets_management":
        has_template = (root / ".env.example").exists()
        gitignore = _read_text(root / ".gitignore")
        passed = has_template and (".env" in gitignore)
        return repo_score(passed, "Secrets management baseline present" if passed else "Secrets management baseline incomplete")

    if criterion_id == "issue_templates":
        passed = (root / ".github" / "ISSUE_TEMPLATE").is_dir()
        return repo_score(passed, "Issue templates found" if passed else "Issue templates not found")

    if criterion_id == "issue_labeling_system":
        if not _gh_auth_ok(ctx):
            return repo_score(False, "GitHub CLI is not authenticated, labeling system cannot be verified")
        labels = ctx.run(["gh", "label", "list", "--limit", "50"], timeout=8)
        passed = labels.exit_code == 0 and bool(labels.stdout.strip())
        return repo_score(passed, "Repository labels detected" if passed else "No label system detected")

    if criterion_id == "backlog_health":
        if not _gh_auth_ok(ctx):
            return skip_repo("Skipping: GitHub CLI is not authenticated")
        issues = ctx.run(["gh", "issue", "list", "--state", "open", "--limit", "30", "--json", "title,labels,createdAt"], timeout=10)
        if issues.exit_code != 0:
            return skip_repo("Skipping: unable to query issue backlog")
        try:
            payload = json.loads(issues.stdout or "[]")
        except json.JSONDecodeError:
            return skip_repo("Skipping: unable to parse issue backlog payload")
        if not payload:
            return skip_repo("Skipping: no open issues to score backlog health")
        healthy = [i for i in payload if len(i.get("title", "")) > 10 and i.get("labels")]
        passed = (len(healthy) / len(payload)) >= 0.7
        return repo_score(passed, "Issue backlog health is acceptable" if passed else "Issue backlog health is below threshold")

    if criterion_id == "pr_templates":
        passed = (root / ".github" / "pull_request_template.md").exists() or (root / ".github" / "PULL_REQUEST_TEMPLATE").is_dir()
        return repo_score(passed, "PR template found" if passed else "PR template not found")

    # Should never happen with frozen rubric.
    return repo_score(False, f"No evaluator implemented for {criterion_id}")


def _app_is_service(app_dir: Path, languages: tuple[str, ...]) -> bool:
    if any(lang in languages for lang in ("python", "go", "rust")):
        return True
    if (app_dir / "package.json").exists() and ((app_dir / "server").is_dir() or (app_dir / "api").is_dir()):
        return True
    return False


def _app_has_tests(app_dir: Path) -> bool:
    if (app_dir / "tests").is_dir() or (app_dir / "test").is_dir():
        return True
    for pattern in ("**/*test*.py", "**/*.spec.ts", "**/*.test.ts", "**/*.spec.js", "**/*.test.js"):
        if any(app_dir.glob(pattern)):
            return True
    return False


def _evaluate_application_criterion(ctx: EvaluationContext, criterion_id: str) -> CriterionEvaluation:
    numerator = 0
    applicable_found = False
    evidence: list[str] = []

    for app_path, app in sorted(ctx.discovery.apps.items()):
        app_dir = ctx.discovery.root if app_path == "." else ctx.discovery.root / app_path
        languages = app.languages
        service_app = _app_is_service(app_dir, languages)
        passed = False
        applicable = True

        if criterion_id == "lint_config":
            passed = any((app_dir / name).exists() for name in (".eslintrc", "eslint.config.js", "ruff.toml", ".flake8", "sonar-project.properties"))
            passed = passed or (app_dir / "pyproject.toml").exists() or (app_dir / "package.json").exists()

        elif criterion_id == "type_check":
            py_text = _read_text(app_dir / "pyproject.toml")
            ts_text = _read_text(app_dir / "tsconfig.json")
            passed = ("mypy" in py_text or "pyright" in py_text or "basedpyright" in py_text)
            passed = passed or ("strict" in ts_text and "true" in ts_text.lower())

        elif criterion_id == "formatter":
            passed = any((app_dir / name).exists() for name in (".prettierrc", ".prettierrc.json", "ruff.toml"))
            passed = passed or _contains_any(_read_text(app_dir / "pyproject.toml"), ("ruff", "black"))

        elif criterion_id == "pre_commit_hooks":
            passed = (ctx.repo_root / ".pre-commit-config.yaml").exists() or (ctx.repo_root / ".husky").is_dir()

        elif criterion_id == "strict_typing":
            ts = _read_text(app_dir / "tsconfig.json")
            py = _read_text(app_dir / "pyproject.toml")
            passed = ("\"strict\"" in ts and "true" in ts.lower()) or ("typecheckingmode" in py.lower() and "strict" in py.lower())

        elif criterion_id == "naming_consistency":
            eslint = _read_text(app_dir / "eslint.config.js") + _read_text(app_dir / ".eslintrc")
            passed = "naming-convention" in eslint or "naming" in _read_text(ctx.repo_root / "AGENTS.md").lower()

        elif criterion_id == "cyclomatic_complexity":
            passed = (ctx.repo_root / "sonar-project.properties").exists() or "complexity" in _read_text(app_dir / "eslint.config.js")

        elif criterion_id == "dead_code_detection":
            pkg = _read_text(app_dir / "package.json")
            passed = any(token in pkg for token in ("knip", "depcheck", "ts-prune"))
            passed = passed or (ctx.repo_root / "sonar-project.properties").exists()

        elif criterion_id == "duplicate_code_detection":
            pkg = _read_text(app_dir / "package.json")
            passed = "jscpd" in pkg or (ctx.repo_root / "sonar-project.properties").exists()

        elif criterion_id == "code_modularization":
            source_files = list(app_dir.glob("src/**/*.py")) + list(app_dir.glob("src/**/*.ts"))
            if len(source_files) < 20:
                applicable = False
            else:
                passed = "dependency-cruiser" in _read_text(app_dir / "package.json")
                passed = passed or "import-linter" in _read_text(app_dir / "pyproject.toml")
                passed = passed or (app_dir / "internal").is_dir()

        elif criterion_id == "n_plus_one_detection":
            if not service_app:
                applicable = False
            else:
                passed = ctx.text_search(("nplusone",), within=app_dir)
                passed = passed or ctx.text_search(("dataloader",), within=app_dir)

        elif criterion_id == "heavy_dependency_detection":
            if not any(lang in languages for lang in ("typescript", "javascript")):
                applicable = False
            else:
                pkg = _read_text(app_dir / "package.json")
                passed = any(token in pkg for token in ("bundle-analyzer", "size-limit", "bundlewatch", "rollup-plugin-visualizer"))

        elif criterion_id == "unused_dependencies_detection":
            pkg = _read_text(app_dir / "package.json")
            pyproject = _read_text(app_dir / "pyproject.toml")
            passed = any(token in pkg for token in ("depcheck", "knip", "npm-check"))
            passed = passed or any(token in pyproject for token in ("deptry", "pip-extra-reqs"))
            passed = passed or "go mod tidy" in _read_text(ctx.repo_root / ".github/workflows/ci.yml")

        elif criterion_id == "unit_tests_exist":
            passed = _app_has_tests(app_dir)

        elif criterion_id == "integration_tests_exist":
            passed = any((app_dir / name).exists() for name in ("cypress", "playwright.config.ts", "tests/integration"))
            passed = passed or any(app_dir.glob("**/*integration*.py"))

        elif criterion_id == "unit_tests_runnable":
            if "python" in languages:
                result = ctx.run(["python3", "-m", "pytest", "--collect-only"], cwd=app_dir, timeout=20)
                passed = result.exit_code == 0
            elif any(lang in languages for lang in ("typescript", "javascript")):
                result = ctx.run(["npm", "run", "test", "--", "--help"], cwd=app_dir, timeout=20)
                passed = result.exit_code == 0
            elif "go" in languages:
                result = ctx.run(["go", "test", "./...", "-run", "TestDoesNotExist"], cwd=app_dir, timeout=20)
                passed = result.exit_code in (0, 1)
            elif "rust" in languages:
                result = ctx.run(["cargo", "test", "--", "--help"], cwd=app_dir, timeout=20)
                passed = result.exit_code == 0
            else:
                passed = _app_has_tests(app_dir)

        elif criterion_id == "test_performance_tracking":
            passed = ctx.text_search(("--durations",), within=app_dir)
            passed = passed or ctx.text_search(("buildpulse",), within=app_dir)
            passed = passed or ctx.text_search(("test-report",), within=ctx.repo_root)

        elif criterion_id == "flaky_test_detection":
            passed = ctx.text_search(("rerunfailures",), within=app_dir)
            passed = passed or ctx.text_search(("retry", "test"), within=app_dir)
            if not passed and not _gh_auth_ok(ctx):
                applicable = False

        elif criterion_id == "test_coverage_thresholds":
            passed = ctx.text_search(("cov-fail-under",), within=app_dir)
            passed = passed or ctx.text_search(("coverageThreshold",), within=app_dir)
            passed = passed or ctx.text_search(("sonar.qualitygate.wait",), within=ctx.repo_root)

        elif criterion_id == "test_naming_conventions":
            # Check for consistent test naming: test_*.py for Python, *.spec.ts/*.test.ts for TS/JS
            passed = any(app_dir.glob("**/test_*.py"))
            passed = passed or any(app_dir.glob("**/*.spec.ts")) or any(app_dir.glob("**/*.test.ts"))
            passed = passed or any(app_dir.glob("**/*.spec.js")) or any(app_dir.glob("**/*.test.js"))
            passed = passed or (app_dir / "pytest.ini").exists()

        elif criterion_id == "test_isolation":
            passed = ctx.text_search(("pytest-xdist",), within=app_dir)
            passed = passed or ctx.text_search(("t.parallel",), within=app_dir)
            passed = passed or ctx.text_search(("threads", "vitest"), within=app_dir)

        elif criterion_id == "api_schema_docs":
            if not service_app:
                applicable = False
            else:
                patterns = ("**/*openapi*.json", "**/*openapi*.y*ml", "**/*swagger*.json", "**/*.graphql", "**/*.gql")
                passed = any(any(app_dir.glob(pattern)) for pattern in patterns)
                passed = passed or any(any(ctx.repo_root.glob(pattern)) for pattern in patterns)

        elif criterion_id == "database_schema":
            if not service_app:
                applicable = False
            else:
                passed = any(app_dir.glob("**/models.py")) or any(app_dir.glob("**/migrations/*.py"))
                passed = passed or any(app_dir.glob("**/*.sql")) or (app_dir / "schema.prisma").exists()

        elif criterion_id == "structured_logging":
            pkg = _read_text(app_dir / "package.json")
            pyproject = _read_text(app_dir / "pyproject.toml")
            passed = any(token in pkg for token in ("winston", "pino", "bunyan", "log4js"))
            passed = passed or any(token in pyproject for token in ("structlog", "loguru", "python-json-logger"))
            passed = passed or any(app_dir.glob("**/*logger*.py"))

        elif criterion_id == "distributed_tracing":
            passed = ctx.text_search(("opentelemetry",), within=app_dir)
            passed = passed or ctx.text_search(("x-request-id",), within=app_dir)
            passed = passed or ctx.text_search(("trace_id",), within=app_dir)

        elif criterion_id == "metrics_collection":
            passed = ctx.text_search(("prometheus",), within=app_dir)
            passed = passed or ctx.text_search(("datadog",), within=app_dir)
            passed = passed or ctx.text_search(("newrelic",), within=app_dir)

        elif criterion_id == "code_quality_metrics":
            passed = (ctx.repo_root / "sonar-project.properties").exists()
            if not passed and not _gh_auth_ok(ctx):
                applicable = False

        elif criterion_id == "error_tracking_contextualized":
            passed = ctx.text_search(("sentry",), within=app_dir)
            passed = passed or ctx.text_search(("bugsnag",), within=app_dir)
            passed = passed or ctx.text_search(("rollbar",), within=app_dir)

        elif criterion_id == "alerting_configured":
            passed = ctx.text_search(("pagerduty",), within=app_dir)
            passed = passed or ctx.text_search(("opsgenie",), within=app_dir)
            passed = passed or ctx.text_search(("alert", "rule"), within=app_dir)

        elif criterion_id == "deployment_observability":
            passed = ctx.text_search(("grafana",), within=ctx.repo_root)
            passed = passed or ctx.text_search(("datadog",), within=ctx.repo_root)
            passed = passed or ctx.text_search(("new relic",), within=ctx.repo_root)

        elif criterion_id == "health_checks":
            if not service_app:
                applicable = False
            else:
                passed = ctx.text_search(("health",), within=app_dir)
                passed = passed or ctx.text_search(("readiness",), within=app_dir)
                passed = passed or ((app_dir / "Dockerfile").exists() and "healthcheck" in _read_text(app_dir / "Dockerfile").lower())

        elif criterion_id == "circuit_breakers":
            if not service_app:
                applicable = False
            else:
                passed = ctx.text_search(("circuit", "breaker"), within=app_dir)
                passed = passed or ctx.text_search(("exponential", "backoff"), within=app_dir)

        elif criterion_id == "profiling_instrumentation":
            if not service_app:
                applicable = False
            else:
                passed = ctx.text_search(("pyroscope",), within=app_dir)
                passed = passed or ctx.text_search(("datadog", "apm"), within=app_dir)
                passed = passed or ctx.text_search(("newrelic",), within=app_dir)

        elif criterion_id == "dast_scanning":
            if not service_app:
                applicable = False
            else:
                ci_content = _read_text(ctx.repo_root / ".github/workflows/ci.yml")
                passed = any(token in ci_content.lower() for token in ("owasp", "zap", "stackhawk", "nuclei", "burp"))

        elif criterion_id == "pii_handling":
            if not service_app:
                applicable = False
            else:
                passed = ctx.text_search(("presidio",), within=app_dir)
                passed = passed or ctx.text_search(("pii",), within=app_dir)
                passed = passed or ctx.text_search(("privacy",), within=ctx.repo_root)

        elif criterion_id == "log_scrubbing":
            passed = ctx.text_search(("redact",), within=app_dir)
            passed = passed or ctx.text_search(("sanitize", "log"), within=app_dir)
            passed = passed or ctx.text_search(("mask", "log"), within=app_dir)

        elif criterion_id == "product_analytics_instrumentation":
            passed = ctx.text_search(("mixpanel",), within=app_dir)
            passed = passed or ctx.text_search(("amplitude",), within=app_dir)
            passed = passed or ctx.text_search(("posthog",), within=app_dir)
            passed = passed or ctx.text_search(("ga4",), within=app_dir)

        elif criterion_id == "error_to_insight_pipeline":
            passed = ctx.text_search(("sentry", "github"), within=ctx.repo_root)
            passed = passed or ctx.text_search(("error", "issue", "automation"), within=ctx.repo_root)

        else:
            raise ValueError(f"No application-scope evaluator for {criterion_id}")

        if applicable:
            applicable_found = True
            if passed:
                numerator += 1
            evidence.append(f"{app_path}:{'pass' if passed else 'fail'}")
        else:
            evidence.append(f"{app_path}:n/a")

    if not applicable_found and _criterion_skippable(ctx, criterion_id):
        return skip_app(
            denominator=ctx.app_count,
            rationale="Skipping: criterion not applicable to discovered applications",
            evidence=tuple(evidence),
        )

    return app_score(
        numerator=numerator,
        denominator=ctx.app_count,
        rationale=f"{numerator}/{ctx.app_count} applications passed {criterion_id}",
        evidence=tuple(evidence),
    )
