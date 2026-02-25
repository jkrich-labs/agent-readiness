"""Tests for individual evaluator implementations.

These tests verify that specific criterion evaluators produce correct
pass/fail/skip results given controlled fixtures.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from agent_readiness.discovery import discover_repository
from agent_readiness.evaluators.base import EvaluationContext
from agent_readiness.evaluators.registry import _evaluate_criterion, _git_remote_slug
from agent_readiness.rubric import load_frozen_rubric


@pytest.fixture()
def rubric():
    return load_frozen_rubric("v0.62.1")


def _make_ctx(repo: Path, rubric, execute_commands: bool = False) -> EvaluationContext:
    discovery = discover_repository(repo)
    return EvaluationContext(
        repo_root=repo,
        discovery=discovery,
        rubric=rubric,
        execute_commands=execute_commands,
    )


def _init_git(tmp_path: Path) -> None:
    import subprocess
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init", "--allow-empty"], cwd=tmp_path, check=True, capture_output=True)


# ---------------------------------------------------------------------------
# _git_remote_slug cache bug fix verification
# ---------------------------------------------------------------------------

class TestGitRemoteSlugCache:
    def test_first_call_does_not_short_circuit(self, tmp_path, rubric):
        """Verify the sentinel-based cache fix: first call should compute, not return None."""
        _init_git(tmp_path)
        (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
        ctx = _make_ctx(tmp_path, rubric)

        # Without a remote, should compute and return None (not short-circuit)
        result = _git_remote_slug(ctx)
        assert result is None
        # Key should now be in the cache
        assert "git_remote_slug" in ctx.cache

    def test_cached_none_is_returned_on_second_call(self, tmp_path, rubric):
        _init_git(tmp_path)
        (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
        ctx = _make_ctx(tmp_path, rubric)

        _git_remote_slug(ctx)
        # Second call should hit cache
        result = _git_remote_slug(ctx)
        assert result is None


# ---------------------------------------------------------------------------
# Repository-scope evaluators
# ---------------------------------------------------------------------------

class TestReadme:
    def test_passes_with_readme(self, sample_repo, rubric):
        # Sample README is short; make it long enough (>100 chars)
        (sample_repo / "README.md").write_text("# Sample Repo\n\n" + "Documentation content. " * 10 + "\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "readme")
        assert result.numerator == 1

    def test_fails_without_readme(self, tmp_path, rubric):
        _init_git(tmp_path)
        (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
        ctx = _make_ctx(tmp_path, rubric)
        result = _evaluate_criterion(ctx, "readme")
        assert result.numerator == 0


class TestAgentsMd:
    def test_passes_with_agents_md(self, sample_repo, rubric):
        (sample_repo / "AGENTS.md").write_text("# Agents\n" + "x" * 200)
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "agents_md")
        assert result.numerator == 1

    def test_fails_when_too_short(self, sample_repo, rubric):
        (sample_repo / "AGENTS.md").write_text("# Short\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "agents_md")
        assert result.numerator == 0


class TestDepsPinned:
    def test_passes_with_lockfile(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        # sample_repo doesn't have a lockfile by default, add one
        (sample_repo / "uv.lock").write_text("# lock\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "deps_pinned")
        assert result.numerator == 1

    def test_fails_without_lockfile(self, tmp_path, rubric):
        _init_git(tmp_path)
        (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
        ctx = _make_ctx(tmp_path, rubric)
        result = _evaluate_criterion(ctx, "deps_pinned")
        assert result.numerator == 0


class TestCodeowners:
    def test_passes_with_codeowners(self, sample_repo, rubric):
        (sample_repo / "CODEOWNERS").write_text("* @team\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "codeowners")
        assert result.numerator == 1

    def test_passes_with_github_codeowners(self, sample_repo, rubric):
        (sample_repo / ".github" / "CODEOWNERS").write_text("* @team\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "codeowners")
        assert result.numerator == 1

    def test_fails_without_codeowners(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "codeowners")
        assert result.numerator == 0


class TestGitignoreComprehensive:
    def test_passes_for_python_js_repo(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "gitignore_comprehensive")
        # sample_repo has .env, node_modules, .venv, dist, build
        assert result.numerator == 1

    def test_fails_when_empty(self, tmp_path, rubric):
        _init_git(tmp_path)
        (tmp_path / ".gitignore").write_text("")
        (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
        ctx = _make_ctx(tmp_path, rubric)
        result = _evaluate_criterion(ctx, "gitignore_comprehensive")
        assert result.numerator == 0

    def test_go_repo_doesnt_require_node_modules(self, tmp_path, rubric):
        """Go-only repos should not need node_modules or .venv in .gitignore."""
        _init_git(tmp_path)
        (tmp_path / "go.mod").write_text("module example.com/app\n")
        (tmp_path / ".gitignore").write_text(".env\ndist\n")
        ctx = _make_ctx(tmp_path, rubric)
        result = _evaluate_criterion(ctx, "gitignore_comprehensive")
        assert result.numerator == 1


class TestDevcontainer:
    def test_passes_with_devcontainer(self, sample_repo, rubric):
        (sample_repo / ".devcontainer").mkdir()
        (sample_repo / ".devcontainer" / "devcontainer.json").write_text("{}")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "devcontainer")
        assert result.numerator == 1

    def test_fails_without_devcontainer(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "devcontainer")
        assert result.numerator == 0


class TestEnvTemplate:
    def test_passes_with_env_example(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "env_template")
        assert result.numerator == 1


class TestDependencyUpdateAutomation:
    def test_passes_with_dependabot(self, sample_repo, rubric):
        (sample_repo / ".github" / "dependabot.yml").write_text("version: 2\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "dependency_update_automation")
        assert result.numerator == 1

    def test_passes_with_renovate(self, sample_repo, rubric):
        (sample_repo / "renovate.json").write_text("{}")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "dependency_update_automation")
        assert result.numerator == 1

    def test_fails_without_either(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "dependency_update_automation")
        assert result.numerator == 0


class TestBuildCmdDoc:
    def test_passes_when_documented(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "build_cmd_doc")
        # sample_repo AGENTS.md has "python3 -m pytest" and "npm run build"
        assert result.numerator == 1


class TestPrTemplates:
    def test_passes_with_template_file(self, sample_repo, rubric):
        (sample_repo / ".github" / "pull_request_template.md").write_text("## Description\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "pr_templates")
        assert result.numerator == 1

    def test_fails_without_template(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "pr_templates")
        assert result.numerator == 0


class TestIssueTemplates:
    def test_passes_with_templates_dir(self, sample_repo, rubric):
        (sample_repo / ".github" / "ISSUE_TEMPLATE").mkdir()
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "issue_templates")
        assert result.numerator == 1


class TestSecretsManagement:
    def test_passes_with_env_example_and_gitignore(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "secrets_management")
        assert result.numerator == 1


class TestReleaseAutomation:
    def test_passes_with_deploy_workflow(self, sample_repo, rubric):
        (sample_repo / ".github" / "workflows" / "deploy.yml").write_text(
            "name: Deploy\non: push\njobs:\n  deploy:\n    runs-on: ubuntu-latest\n"
        )
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "release_automation")
        assert result.numerator == 1

    def test_fails_without_deploy_workflow(self, tmp_path, rubric):
        _init_git(tmp_path)
        (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
        ctx = _make_ctx(tmp_path, rubric)
        result = _evaluate_criterion(ctx, "release_automation")
        assert result.numerator == 0


class TestSkills:
    def test_passes_with_valid_skill(self, sample_repo, rubric):
        skill_dir = sample_repo / ".claude" / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("name: my-skill\ndescription: A test skill\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "skills")
        assert result.numerator == 1

    def test_fails_without_skills(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "skills")
        assert result.numerator == 0


# ---------------------------------------------------------------------------
# Application-scope evaluators
# ---------------------------------------------------------------------------

class TestLintConfig:
    def test_passes_with_pyproject(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "lint_config")
        # Both backend (pyproject.toml) and frontend (package.json) have lint markers
        assert result.numerator == result.denominator

    def test_fails_in_bare_repo(self, tmp_path, rubric):
        _init_git(tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("pass\n")
        ctx = _make_ctx(tmp_path, rubric)
        result = _evaluate_criterion(ctx, "lint_config")
        assert result.numerator == 0


class TestTypeCheck:
    def test_passes_with_strict_tsconfig(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "type_check")
        # frontend has strict tsconfig
        assert result.numerator >= 1


class TestFormatter:
    def test_passes_with_prettierrc(self, sample_repo, rubric):
        (sample_repo / "frontend" / ".prettierrc").write_text("{}")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "formatter")
        assert result.numerator >= 1


class TestPreCommitHooks:
    def test_passes_with_pre_commit_config(self, sample_repo, rubric):
        (sample_repo / ".pre-commit-config.yaml").write_text("repos: []\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "pre_commit_hooks")
        assert result.numerator == result.denominator

    def test_passes_with_husky(self, sample_repo, rubric):
        (sample_repo / ".husky").mkdir()
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "pre_commit_hooks")
        assert result.numerator == result.denominator

    def test_fails_without_hooks(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "pre_commit_hooks")
        assert result.numerator == 0


class TestUnitTestsExist:
    def test_passes_with_test_dir(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "unit_tests_exist")
        # backend has tests/ dir, frontend has .spec.ts file
        assert result.numerator == result.denominator


class TestTestNamingConventions:
    def test_passes_with_test_files(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "test_naming_conventions")
        # backend has test_basic.py, frontend has main.spec.ts
        assert result.numerator == result.denominator

    def test_fails_without_test_files(self, tmp_path, rubric):
        _init_git(tmp_path)
        (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
        (tmp_path / "main.py").write_text("pass\n")
        ctx = _make_ctx(tmp_path, rubric)
        result = _evaluate_criterion(ctx, "test_naming_conventions")
        assert result.numerator == 0


class TestDatabaseSchema:
    def test_passes_with_models(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "database_schema")
        # backend has models.py and is a service app (python)
        assert result.numerator >= 1


class TestStructuredLogging:
    def test_passes_with_logger_file(self, sample_repo, rubric):
        (sample_repo / "backend" / "logger.py").write_text("import logging\n")
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "structured_logging")
        assert result.numerator >= 1


class TestIntegrationTestsExist:
    def test_passes_with_integration_dir(self, sample_repo, rubric):
        (sample_repo / "backend" / "tests" / "integration").mkdir()
        ctx = _make_ctx(sample_repo, rubric)
        result = _evaluate_criterion(ctx, "integration_tests_exist")
        assert result.numerator >= 1


# ---------------------------------------------------------------------------
# text_search content searching (verifying Fix 2)
# ---------------------------------------------------------------------------

class TestTextSearchContent:
    def test_finds_token_in_file_content(self, sample_repo, rubric):
        """text_search should find tokens inside file contents, not just paths."""
        (sample_repo / "backend" / "sentry_config.toml").write_text(
            "[sentry]\ndsn = 'https://sentry.io/example'\n"
        )
        ctx = _make_ctx(sample_repo, rubric)
        # Token "sentry" should be found in the file content
        assert ctx.text_search(("sentry",), within=sample_repo / "backend")

    def test_finds_multi_token_in_content(self, sample_repo, rubric):
        (sample_repo / "backend" / "config.py").write_text(
            "FEATURE_FLAG_PROVIDER = 'launchdarkly'\n"
        )
        ctx = _make_ctx(sample_repo, rubric)
        assert ctx.text_search(("launchdarkly",), within=sample_repo / "backend")

    def test_does_not_find_absent_token(self, sample_repo, rubric):
        ctx = _make_ctx(sample_repo, rubric)
        assert not ctx.text_search(("nonexistent_xyzzy_token",), within=sample_repo / "backend")
