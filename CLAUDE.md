# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Local-only clone of Droid `/readiness-report` — evaluates a repository against a frozen 81-criterion rubric (Droid v0.62.1) and produces readiness artifacts. No Factory API integration; everything runs locally.

## Commands

```bash
# Install (editable, with dev deps)
uv sync --extra dev

# Run all tests
uv run python -m pytest

# Run a single test file
uv run python -m pytest tests/test_scoring.py

# Run a single test
uv run python -m pytest tests/test_scoring.py::test_pass_rate_excludes_skipped -v

# Run the CLI against a repo
agent-readiness run --repo . --out-dir ./out

# Explain a criterion
agent-readiness explain lint_config

# Validate rubric coverage
agent-readiness self-check
```

## Architecture

The pipeline flows: **CLI → Runner → Discovery + Registry → Evaluators → Scoring → Artifacts**

### Frozen Rubric (`rubric/droid/v0.62.1/`)
Source of truth for all 81 criteria. Four files: `criteria_order.txt`, `criteria_scope.json`, `scoring_rules.json`, `provenance.json`. Loaded by `rubric.py` with strict count/order/scope validation (43 repository-scope + 38 application-scope = 81 total). Changing these files will break integrity tests.

### Core Engine (`src/agent_readiness/`)
- **`runner.py`** — `ReadinessRunner` orchestrates the full pipeline: discovery → build registry → evaluate all 81 criteria in deterministic order → validate envelope shape → return `ReadinessReportEnvelope`.
- **`discovery.py`** — Detects apps (looks in `backend/`, `frontend/`, `api/`, `apps/*`, etc.) and their languages (Python, TypeScript, JavaScript, Go, Rust). Falls back to repo root as single app.
- **`models.py`** — Frozen dataclasses: `CriterionEvaluation` (numerator/denominator/rationale/evidence), `ReadinessReportEnvelope`, `AppDescription`.
- **`scoring.py`** — `pass_rate()` averages numerator/denominator ratios, excluding skipped (null numerator) criteria. `level_from_pass_rate()` maps to levels 1–5 in 0.2 bands.
- **`validator.py`** — Post-evaluation shape validation: exactly 81 keys, repo-scope denominator=1, app-scope denominator=app_count, numerator bounds.
- **`artifacts.py`** — Writes three output files: `readiness-report.json`, `readiness-report.md`, `readiness-actions.json`.

### Evaluator System (`src/agent_readiness/evaluators/`)
- **`base.py`** — `EvaluationContext` provides helpers (`has_any_paths`, `glob_exists`, `text_search`, `run`) and builds a file index at init. `text_search` first checks file paths, then reads file contents for matching tokens. Also defines score helpers: `repo_score`, `skip_repo`, `app_score`, `skip_app`.
- **`registry.py`** — `build_registry()` creates one `_FunctionEvaluator` per criterion. All 81 evaluators are implemented inline as a big if-chain in `_evaluate_repository_criterion` and `_evaluate_application_criterion`. Repository-scope criteria return 0/1 or skip. Application-scope criteria iterate all discovered apps and aggregate pass counts.

### Key Conventions
- **Skippable criteria**: `numerator: None` means the criterion was skipped (not applicable). Skipped criteria are excluded from pass-rate denominator.
- **Repository vs application scope**: Repository-scope always has `denominator=1`. Application-scope has `denominator=len(apps)`.
- **Command execution**: Evaluators can shell out via `EvaluationContext.run()` (wraps `command_runner.run_command`). Disabled with `--no-command-execution`.
- **GitHub CLI dependency**: Several criteria (branch_protection, secret_scanning, fast_ci_feedback, etc.) require `gh auth status` to succeed; they skip gracefully when gh is not authenticated.

## Adding a New Evaluator

New criteria cannot be added without also updating the frozen rubric files. If modifying evaluator logic for an existing criterion, add the check logic to `_evaluate_repository_criterion` or `_evaluate_application_criterion` in `registry.py`. The test `test_registry_coverage.py` verifies every rubric criterion maps to an evaluator.

## Test Fixtures

`tests/conftest.py` provides a `sample_repo` fixture — a minimal git repo in `tmp_path` with backend (Python) and frontend (TypeScript) apps, `.github/workflows/ci.yml`, and standard files. Most evaluator tests use this fixture.
