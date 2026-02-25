# HTML Readiness Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a 4th artifact (`readiness-dashboard.html`) to the pipeline — a self-contained HTML dashboard with readiness results, filterable criteria, and copy-pasteable LLM remediation prompts for every failing criterion.

**Architecture:** Standalone HTML template (`src/agent_readiness/templates/dashboard.html`) with three JSON placeholder slots. Python reads the template, injects report data + rubric metadata + 81 criterion-specific remediation templates (from `rubric/droid/v0.62.1/remediation/*.md`), and writes the final HTML to `out_dir`. Client-side vanilla JS + Tailwind CSS + Chart.js render the dashboard.

**Tech Stack:** Python (artifacts/rubric), HTML/CSS/JS (Tailwind via CDN, Chart.js via CDN, vanilla JS)

---

### Task 1: Seed Remediation Template Directory

Create the directory structure and 3 seed `.md` files to unblock testing in Tasks 2-3.

**Files:**
- Create: `rubric/droid/v0.62.1/remediation/lint_config.md`
- Create: `rubric/droid/v0.62.1/remediation/readme.md`
- Create: `rubric/droid/v0.62.1/remediation/branch_protection.md`

**Step 1: Create directory**

```bash
mkdir -p rubric/droid/v0.62.1/remediation
```

**Step 2: Create `lint_config.md`**

This is a Level 1, application-scope criterion. Full example of the remediation template format:

```markdown
---
signal_name: Lint Configuration
---

## Criterion-Specific Fix Guidance

- **Python projects**: Install and configure `ruff` (preferred) or `flake8`. Create a `ruff.toml` or `pyproject.toml` `[tool.ruff]` section with sensible defaults. At minimum enable `E` (pycodestyle errors) and `F` (pyflakes) rule sets. Consider also enabling `I` (isort), `N` (pep8-naming), and `UP` (pyupgrade).
- **TypeScript/JavaScript projects**: Install `eslint` and create `.eslintrc.json` or `eslint.config.js`. Use `@typescript-eslint/recommended` for TS projects or `eslint:recommended` for JS. Enable `no-unused-vars`, `no-undef`, and `consistent-return` at minimum.
- **SonarQube alternative**: If SonarQube is configured for the project (`sonar-project.properties` exists), verify the quality profile includes lint rules and is not explicitly disabled.
- Add lint commands to `package.json` scripts or `pyproject.toml` `[project.scripts]`.
- Integrate linting into CI pipeline (add a lint step to `.github/workflows/ci.yml`).

## Criterion-Specific Exploration Steps

- Check for existing lint config files: `.eslintrc*`, `eslint.config.*`, `ruff.toml`, `pyproject.toml` `[tool.ruff]`/`[tool.flake8]`, `setup.cfg`, `sonar-project.properties`
- Check `package.json` for eslint in devDependencies and lint scripts
- Check CI workflows for lint steps

## Criterion-Specific Verification Steps

- Run the linter: `npx eslint .` or `ruff check .` and confirm it executes without config errors
- Verify the config file is valid and contains real rules (not an empty or disabled config)
```

**Step 3: Create `readme.md`**

```markdown
---
signal_name: README
---

## Criterion-Specific Fix Guidance

- Create or enhance `README.md` at the repository root.
- Must include: project name, one-paragraph description of what the project does, setup/installation instructions, and basic usage examples.
- If the repo has multiple apps (monorepo), the root README should explain the repo structure and link to app-specific READMEs.
- Include build and test commands so developers (human or AI) can get started quickly.
- Keep it concise — a good README is 50-200 lines, not a novel.

## Criterion-Specific Exploration Steps

- Check if `README.md` exists at the repository root
- If it exists, check whether it contains setup instructions and usage information
- Check for app-level READMEs in subdirectories

## Criterion-Specific Verification Steps

- Confirm `README.md` exists and has substantive content (>100 characters, not just a title)
- Verify it mentions at least one build or test command
```

**Step 4: Create `branch_protection.md`**

```markdown
---
signal_name: Branch Protection
---

## Criterion-Specific Fix Guidance

- Enable branch protection rules on the default branch (usually `main` or `master`).
- Use GitHub rulesets (preferred, newer) or legacy branch protection settings.
- **Via GitHub CLI**: `gh api repos/{owner}/{repo}/rulesets -X POST` with a ruleset that requires pull request reviews and status checks to pass.
- **Via GitHub web UI**: Settings → Branches → Add branch protection rule → check "Require a pull request before merging" and "Require status checks to pass before merging".
- At minimum require: 1 approving review, status checks passing, and branch is up to date before merging.
- For legacy branch protection: `gh api repos/{owner}/{repo}/branches/main/protection -X PUT` with appropriate JSON body.

## Criterion-Specific Exploration Steps

- Determine the default branch name: `git symbolic-ref refs/remotes/origin/HEAD`
- Check current branch protection status: `gh api repos/{owner}/{repo}/branches/{branch}/protection` (will 404 if not configured)
- Check for GitHub rulesets: `gh api repos/{owner}/{repo}/rulesets`
- Verify `gh auth status` succeeds (required for API calls)

## Criterion-Specific Verification Steps

- Run `gh api repos/{owner}/{repo}/branches/{branch}/protection` and confirm it returns protection rules (not 404)
- Verify the response includes `required_pull_request_reviews` and `required_status_checks`
```

**Step 5: Commit**

```bash
git add rubric/droid/v0.62.1/remediation/
git commit -m "feat: seed remediation template directory with 3 examples"
```

---

### Task 2: TDD `load_remediation_templates()` in rubric.py

**Files:**
- Test: `tests/test_rubric_loader.py` (extend existing)
- Modify: `src/agent_readiness/rubric.py`

**Step 1: Write the failing tests**

Add to `tests/test_rubric_loader.py`:

```python
def test_load_remediation_templates_returns_dict_of_strings() -> None:
    from agent_readiness.rubric import load_remediation_templates

    templates = load_remediation_templates("v0.62.1")
    assert isinstance(templates, dict)
    assert all(isinstance(v, str) for v in templates.values())
    assert all(isinstance(k, str) for k in templates.keys())
    # After all 81 are authored, this will be 81
    assert len(templates) > 0


def test_load_remediation_templates_keys_are_subset_of_rubric() -> None:
    from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates

    rubric = load_frozen_rubric("v0.62.1")
    templates = load_remediation_templates("v0.62.1")
    assert set(templates.keys()).issubset(set(rubric.criteria_order))


def test_load_remediation_templates_raises_on_bad_version() -> None:
    from agent_readiness.rubric import load_remediation_templates

    with pytest.raises((FileNotFoundError, ValueError)):
        load_remediation_templates("v99.99.99")
```

**Step 2: Run tests to verify they fail**

```bash
uv run python -m pytest tests/test_rubric_loader.py -v -k "remediation"
```

Expected: FAIL — `ImportError: cannot import name 'load_remediation_templates'`

**Step 3: Implement `load_remediation_templates()` in `rubric.py`**

Add to `src/agent_readiness/rubric.py`:

```python
def load_remediation_templates(
    version: str = DEFAULT_RUBRIC_VERSION,
    rubric_root: Path | None = None,
) -> dict[str, str]:
    base = (rubric_root or _default_rubric_root()) / version / "remediation"
    if not base.is_dir():
        raise FileNotFoundError(f"Remediation directory not found: {base}")

    templates: dict[str, str] = {}
    for md_file in sorted(base.glob("*.md")):
        criterion_id = md_file.stem
        templates[criterion_id] = md_file.read_text(encoding="utf-8")

    return templates
```

**Step 4: Run tests to verify they pass**

```bash
uv run python -m pytest tests/test_rubric_loader.py -v -k "remediation"
```

Expected: PASS

**Step 5: Run full test suite to check for regressions**

```bash
uv run python -m pytest
```

Expected: All existing tests still pass.

**Step 6: Commit**

```bash
git add src/agent_readiness/rubric.py tests/test_rubric_loader.py
git commit -m "feat: add load_remediation_templates() to rubric module"
```

---

### Task 3: TDD Remediation Coverage Test

This test will initially fail (only 3 of 81 templates exist). It serves as the gate that ensures Task 4 is complete.

**Files:**
- Create: `tests/test_remediation_coverage.py`

**Step 1: Write the coverage test**

```python
"""Verify every rubric criterion has a corresponding remediation template."""
from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates


def test_remediation_templates_cover_all_81_criteria() -> None:
    rubric = load_frozen_rubric("v0.62.1")
    templates = load_remediation_templates("v0.62.1")
    rubric_ids = set(rubric.criteria_order)
    template_ids = set(templates.keys())

    missing = rubric_ids - template_ids
    orphans = template_ids - rubric_ids

    assert not missing, f"Missing remediation templates: {sorted(missing)}"
    assert not orphans, f"Orphan remediation templates (no matching criterion): {sorted(orphans)}"
    assert len(templates) == 81


def test_remediation_templates_have_signal_name() -> None:
    """Each template must have a signal_name in its YAML frontmatter."""
    templates = load_remediation_templates("v0.62.1")
    for criterion_id, content in templates.items():
        assert "signal_name:" in content, (
            f"Remediation template {criterion_id}.md missing signal_name in frontmatter"
        )


def test_remediation_templates_have_fix_guidance() -> None:
    """Each template must include criterion-specific fix guidance."""
    templates = load_remediation_templates("v0.62.1")
    for criterion_id, content in templates.items():
        assert "## Criterion-Specific Fix Guidance" in content, (
            f"Remediation template {criterion_id}.md missing fix guidance section"
        )
```

**Step 2: Run test to confirm it fails (only 3 of 81 exist)**

```bash
uv run python -m pytest tests/test_remediation_coverage.py -v
```

Expected: FAIL — `Missing remediation templates: [78 criterion IDs]`

**Step 3: Commit the test (it will fail until Task 4 completes)**

```bash
git add tests/test_remediation_coverage.py
git commit -m "test: add remediation template coverage test (will pass after authoring)"
```

---

### Task 4: Author All 81 Remediation Templates

Create the remaining 78 `.md` files in `rubric/droid/v0.62.1/remediation/`. Each file follows the format established in Task 1.

**Files:**
- Create: `rubric/droid/v0.62.1/remediation/{criterion_id}.md` × 78 remaining files

Every file MUST have:
1. YAML frontmatter with `signal_name` (human-readable criterion name)
2. `## Criterion-Specific Fix Guidance` — concrete, actionable bullet points
3. `## Criterion-Specific Exploration Steps` — what to look for in the repo
4. `## Criterion-Specific Verification Steps` — how to confirm the fix works

**Authoring depth by level:**
- Level 1 (6 total, 4 remaining: `type_check`, `formatter`, `env_template`, `unit_tests_exist`, `gitignore_comprehensive`): Detailed, step-by-step. These are basics — be very specific about tools and configs.
- Level 2 (22 total): Solid guidance with tool recommendations. Criteria: `build_cmd_doc`, `deps_pinned`, `vcs_cli_tools`, `automated_pr_review`, `pre_commit_hooks`, `strict_typing`, `devcontainer`, `local_services_setup`, `runbooks_documented`, `codeowners`, `automated_security_review`, `dependency_update_automation`, `secrets_management`, `issue_templates`, `issue_labeling_system`, `pr_templates`, `monorepo_tooling`, `unit_tests_runnable`, `test_coverage_thresholds`, `database_schema`, `structured_logging`, `error_tracking_contextualized`.
- Level 3 (24 total): Good guidance. Criteria: `large_file_detection`, `tech_debt_tracking`, `agentic_development`, `single_command_setup`, `release_notes_automation`, `release_automation`, `dead_feature_flag_detection`, `skills`, `documentation_freshness`, `service_flow_documented`, `secret_scanning`, `naming_consistency`, `dead_code_detection`, `duplicate_code_detection`, `unused_dependencies_detection`, `integration_tests_exist`, `test_naming_conventions`, `distributed_tracing`, `metrics_collection`, `alerting_configured`, `health_checks`, `pii_handling`, `log_scrubbing`, `product_analytics_instrumentation`.
- Level 4 (21 total): Adequate, directional. Criteria: `fast_ci_feedback`, `build_performance_tracking`, `deployment_frequency`, `feature_flag_infrastructure`, `progressive_rollout`, `rollback_automation`, `version_drift_detection`, `agents_md_validation`, `devcontainer_runnable`, `privacy_compliance`, `backlog_health`, `code_modularization`, `n_plus_one_detection`, `heavy_dependency_detection`, `test_performance_tracking`, `flaky_test_detection`, `test_isolation`, `code_quality_metrics`, `deployment_observability`, `circuit_breakers`, `profiling_instrumentation`, `dast_scanning`.
- Level 5 (2 total): `cyclomatic_complexity`, `error_to_insight_pipeline`.

**Step 1: Author repository-scope templates (40 remaining)**

Create each file in `rubric/droid/v0.62.1/remediation/`. Use the rubric descriptions from `criteria_scope.json` (reproduced below for reference) to write accurate, specific guidance for each criterion.

Repository-scope criteria needing templates (40 remaining, `readme` and `branch_protection` already done):
`large_file_detection`, `tech_debt_tracking`, `build_cmd_doc`, `deps_pinned`, `vcs_cli_tools`, `automated_pr_review`, `agentic_development`, `fast_ci_feedback`, `build_performance_tracking`, `deployment_frequency`, `single_command_setup`, `feature_flag_infrastructure`, `release_notes_automation`, `progressive_rollout`, `rollback_automation`, `monorepo_tooling`, `version_drift_detection`, `release_automation`, `dead_feature_flag_detection`, `agents_md`, `automated_doc_generation`, `skills`, `documentation_freshness`, `service_flow_documented`, `agents_md_validation`, `devcontainer`, `env_template`, `local_services_setup`, `devcontainer_runnable`, `runbooks_documented`, `secret_scanning`, `codeowners`, `automated_security_review`, `dependency_update_automation`, `gitignore_comprehensive`, `privacy_compliance`, `secrets_management`, `issue_templates`, `issue_labeling_system`, `backlog_health`, `pr_templates`.

**Step 2: Author application-scope templates (37 remaining)**

Application-scope criteria needing templates (37 remaining, `lint_config` already done):
`type_check`, `formatter`, `pre_commit_hooks`, `strict_typing`, `naming_consistency`, `cyclomatic_complexity`, `dead_code_detection`, `duplicate_code_detection`, `code_modularization`, `n_plus_one_detection`, `heavy_dependency_detection`, `unused_dependencies_detection`, `unit_tests_exist`, `integration_tests_exist`, `unit_tests_runnable`, `test_performance_tracking`, `flaky_test_detection`, `test_coverage_thresholds`, `test_naming_conventions`, `test_isolation`, `api_schema_docs`, `database_schema`, `structured_logging`, `distributed_tracing`, `metrics_collection`, `code_quality_metrics`, `error_tracking_contextualized`, `alerting_configured`, `deployment_observability`, `health_checks`, `circuit_breakers`, `profiling_instrumentation`, `dast_scanning`, `pii_handling`, `log_scrubbing`, `product_analytics_instrumentation`, `error_to_insight_pipeline`.

**Step 3: Run remediation coverage test**

```bash
uv run python -m pytest tests/test_remediation_coverage.py -v
```

Expected: PASS — all 81 templates present, each has `signal_name` and fix guidance.

**Step 4: Commit**

```bash
git add rubric/droid/v0.62.1/remediation/
git commit -m "feat: author all 81 criterion-specific remediation templates"
```

---

### Task 5: Create HTML Dashboard Template Shell

**Files:**
- Create: `src/agent_readiness/templates/dashboard.html`

**Step 1: Verify directory exists**

```bash
ls src/agent_readiness/templates/ 2>/dev/null || echo "need to create"
```

**Step 2: Create the HTML template**

Create `src/agent_readiness/templates/dashboard.html` — a complete, self-contained HTML file with:

- CDN references: Tailwind CSS play CDN (`<script src="https://cdn.tailwindcss.com"></script>`), Chart.js (`<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`)
- Three data placeholder slots in a `<script>` tag:
  ```html
  <script>
    const REPORT_DATA = /*__REPORT_DATA__*/ {} /*__END__*/;
    const RUBRIC_DATA = /*__RUBRIC_DATA__*/ {} /*__END__*/;
    const REMEDIATION_DATA = /*__REMEDIATION_DATA__*/ {} /*__END__*/;
  </script>
  ```
- Layout structure: fixed sidebar nav + scrollable main content
- Six sections with `id` attributes for anchor navigation:
  - `#summary` — Summary header with pass rate ring, level badge, stat cards
  - `#levels` — Level breakdown bar chart (Chart.js)
  - `#scopes` — Scope breakdown cards (repo vs app)
  - `#criteria` — Filterable/sortable criteria table
  - `#actions` — Priority action cards
  - `#remediation` — Remediation drawer (hidden by default, slides in on selection)
- Sidebar nav with anchor links + mini status (pass rate + level)
- Color system: green (#22c55e pass), red (#ef4444 fail), gray (#6b7280 skip), level colors (L1 #3b82f6, L2 #8b5cf6, L3 #f59e0b, L4 #f97316, L5 #ef4444)
- Dark sidebar (`bg-gray-900 text-white`), light main (`bg-gray-50`)

Client-side JS modules (all inline):

```javascript
// computeStats(reportData, rubricData) → { passRate, level, passed, failed, skipped,
//   levelBreakdown: [{level, total, passed, rate}],
//   scopeBreakdown: {repository: {total, passed, failed, skipped}, application: {...}} }

// renderSummary(stats, reportData) — fills #summary section

// renderCharts(stats) — creates Chart.js horizontal bar in #levels canvas

// renderCriteriaTable(reportData, rubricData) — builds filterable table in #criteria
//   - Filter buttons for status (all/pass/fail/skip), level (1-5), scope (repo/app)
//   - Sort by clicking column headers
//   - Row click calls showRemediation(criterionId)

// renderActions(reportData, rubricData) — builds priority cards in #actions
//   - Failed criteria sorted by (level asc, ratio asc)
//   - Each card has "Fix This" button → showRemediation(criterionId)

// renderScopeBreakdown(stats, reportData) — fills #scopes section

// showRemediation(criterionId) — opens remediation drawer
//   - Reads REMEDIATION_DATA[criterionId] for criterion-specific template
//   - Reads RUBRIC_DATA.criteria[criterionId] for description
//   - Reads REPORT_DATA.report[criterionId] for score/rationale/evidence
//   - Assembles full prompt with dynamic wrapper + static template content
//   - Renders prompt in styled pre/code block
//   - "Copy to Clipboard" button with visual feedback

// assemblePrompt(criterionId) → string — builds the full LLM prompt:
//   1. Parse signal_name from YAML frontmatter of remediation template
//   2. Wrap with standard header: "[Readiness Fix] {signal_name}"
//   3. Add system-reminder wrapper with failing signal details
//   4. Insert criterion-specific sections from .md content
//   5. Add standard task instructions and quality standards

// copyToClipboard(text) — navigator.clipboard.writeText + toast notification

// init() — called on DOMContentLoaded, orchestrates all render functions
```

Prompt assembly wrapper (hardcoded in JS `assemblePrompt` function):

```
[Readiness Fix] {signal_name}

Fix the failing signal: {signal_name} ([{numerator}/{denominator}])

<system-reminder>
You are fixing an Agent Readiness signal. Agent Readiness evaluates how well
a repository supports autonomous AI agents working on the codebase.

## Failing Signal

**Signal**: {signal_name}
**Score**: [{numerator}/{denominator}]
**Description**: {rubric_description}
**Why it failed**: {rationale}

## Original Signal Evaluation Criteria

The agent readiness report evaluated this signal using these instructions:

{rubric_description_full}

{criterion_specific_content_from_md}

## Your Task

1. Explore the repository to understand the current state related to this signal
2. {exploration_steps_from_md}
3. Make **substantive improvements** to the codebase that genuinely address the signal
4. {verification_steps_from_md}
5. Keep changes focused on this signal - don't refactor unrelated code
6. When done with code changes, open a PULL REQUEST with the changes and return the PR URL

## CRITICAL: Quality Standards

Your fix must **genuinely improve the codebase**. Do NOT use workarounds or shortcuts:

- **NO** empty placeholder files (e.g., empty test files, stub configs)
- **NO** minimal implementations that technically pass but provide no real value
- **NO** disabling checks or adding skip markers to pass validation
- **NO** trivial changes that game the metric without improving quality

## Completion

- IMPORTANT: When finishing work and you made code changes, open a PULL REQUEST with the changes and return the PR URL
- Provide a succinct summary of what you changed and why it genuinely improves the codebase
</system-reminder>
```

**Step 3: Verify template opens in browser (manual)**

Open `src/agent_readiness/templates/dashboard.html` in a browser. It should render the shell layout with empty state (no data).

**Step 4: Commit**

```bash
git add src/agent_readiness/templates/
git commit -m "feat: create HTML dashboard template with all six sections"
```

---

### Task 6: TDD `write_html_dashboard()` in artifacts.py

**Files:**
- Test: `tests/test_artifacts.py` (extend existing)
- Modify: `src/agent_readiness/artifacts.py`

**Step 1: Write failing tests**

Add to `tests/test_artifacts.py`:

```python
def test_write_html_dashboard_creates_file(tmp_path, sample_repo) -> None:
    from agent_readiness.artifacts import write_html_dashboard
    from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates
    from agent_readiness.runner import ReadinessRunner, RunOptions

    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    rubric = load_frozen_rubric()
    templates = load_remediation_templates()

    path = write_html_dashboard(envelope, rubric, templates, out)
    assert path.exists()
    assert path.name == "readiness-dashboard.html"


def test_write_html_dashboard_contains_embedded_data(tmp_path, sample_repo) -> None:
    from agent_readiness.artifacts import write_html_dashboard
    from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates
    from agent_readiness.runner import ReadinessRunner, RunOptions

    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    rubric = load_frozen_rubric()
    templates = load_remediation_templates()

    path = write_html_dashboard(envelope, rubric, templates, out)
    html = path.read_text(encoding="utf-8")

    # Verify data was injected (not empty defaults)
    assert envelope.repoUrl in html
    assert "lint_config" in html  # criterion ID appears in injected data
    assert "readiness-dashboard" in html.lower() or "Readiness Dashboard" in html


def test_write_html_dashboard_is_valid_html(tmp_path, sample_repo) -> None:
    from agent_readiness.artifacts import write_html_dashboard
    from agent_readiness.rubric import load_frozen_rubric, load_remediation_templates
    from agent_readiness.runner import ReadinessRunner, RunOptions

    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    rubric = load_frozen_rubric()
    templates = load_remediation_templates()

    path = write_html_dashboard(envelope, rubric, templates, out)
    html = path.read_text(encoding="utf-8")

    assert html.strip().startswith("<!DOCTYPE html>") or html.strip().startswith("<!doctype html>")
    assert "</html>" in html
    assert "<script>" in html
```

**Step 2: Run tests to verify they fail**

```bash
uv run python -m pytest tests/test_artifacts.py -v -k "dashboard"
```

Expected: FAIL — `ImportError: cannot import name 'write_html_dashboard'`

**Step 3: Implement `write_html_dashboard()`**

Add to `src/agent_readiness/artifacts.py`:

```python
import re
from importlib.resources import files as pkg_files


def _rubric_to_json_dict(rubric: FrozenRubric) -> dict[str, object]:
    """Serialize rubric definitions for embedding in HTML."""
    return {
        "criteria": {
            cid: {
                "scope": d.scope,
                "level": d.level,
                "skippable": d.skippable,
                "description": d.description,
            }
            for cid, d in rubric.definitions.items()
        },
        "criteria_order": list(rubric.criteria_order),
        "repository_scope": sorted(rubric.repository_scope),
        "application_scope": sorted(rubric.application_scope),
    }


def _inject_data(template: str, marker: str, data: str) -> str:
    """Replace /*__MARKER__*/ {} /*__END__*/ with /*__MARKER__*/ {data} /*__END__*/."""
    pattern = rf"/\*{re.escape(marker)}\*/.*?/\*__END__\*/"
    replacement = f"/*{marker}*/ {data} /*__END__*/"
    return re.sub(pattern, replacement, template, count=1, flags=re.DOTALL)


def write_html_dashboard(
    envelope: ReadinessReportEnvelope,
    rubric: FrozenRubric,
    remediation_templates: dict[str, str],
    out_dir: Path,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Read template
    template_path = Path(__file__).parent / "templates" / "dashboard.html"
    template = template_path.read_text(encoding="utf-8")

    # Inject data
    report_json = json.dumps(_report_to_json_dict(envelope), sort_keys=True)
    rubric_json = json.dumps(_rubric_to_json_dict(rubric), sort_keys=True)
    remediation_json = json.dumps(remediation_templates, sort_keys=True)

    html = _inject_data(template, "__REPORT_DATA__", report_json)
    html = _inject_data(html, "__RUBRIC_DATA__", rubric_json)
    html = _inject_data(html, "__REMEDIATION_DATA__", remediation_json)

    dashboard_path = out_dir / "readiness-dashboard.html"
    dashboard_path.write_text(html, encoding="utf-8")
    return dashboard_path
```

**Step 4: Run tests to verify they pass**

```bash
uv run python -m pytest tests/test_artifacts.py -v -k "dashboard"
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/agent_readiness/artifacts.py tests/test_artifacts.py
git commit -m "feat: add write_html_dashboard() with data injection"
```

---

### Task 7: Integrate Dashboard Into Pipeline

Update `write_artifacts()` to produce 4 artifacts and update CLI output.

**Files:**
- Modify: `src/agent_readiness/artifacts.py` (line 102 `write_artifacts`)
- Modify: `src/agent_readiness/cli.py` (line 38 `_cmd_run`)
- Test: `tests/test_artifacts.py` (update existing test)
- Test: `tests/test_cli.py` (update existing test)

**Step 1: Update `write_artifacts()` signature and return type**

In `src/agent_readiness/artifacts.py`, change `write_artifacts` to:

```python
def write_artifacts(
    envelope: ReadinessReportEnvelope,
    rubric: FrozenRubric,
    out_dir: Path,
    remediation_templates: dict[str, str] | None = None,
) -> tuple[Path, Path, Path, Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)

    report_json_path = out_dir / "readiness-report.json"
    report_md_path = out_dir / "readiness-report.md"
    actions_json_path = out_dir / "readiness-actions.json"

    report_json_path.write_text(
        json.dumps(_report_to_json_dict(envelope), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_md_path.write_text(_build_markdown(envelope, rubric), encoding="utf-8")
    actions_json_path.write_text(
        json.dumps({"actions": _build_actions(envelope, rubric)}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    dashboard_path = None
    if remediation_templates is not None:
        dashboard_path = write_html_dashboard(envelope, rubric, remediation_templates, out_dir)

    return report_json_path, report_md_path, actions_json_path, dashboard_path
```

**Step 2: Update CLI to load remediation templates and include dashboard**

In `src/agent_readiness/cli.py`, update `_cmd_run`:

```python
from .rubric import DEFAULT_RUBRIC_VERSION, load_frozen_rubric, load_remediation_templates

def _cmd_run(args: argparse.Namespace) -> int:
    runner = ReadinessRunner(
        repo_path=args.repo,
        repo_url=args.repo_url,
        rubric_version=args.rubric_version,
        options=RunOptions(execute_commands=not args.no_command_execution),
    )
    envelope = runner.evaluate()
    remediation = load_remediation_templates(args.rubric_version)
    report_json, report_md, actions_json, dashboard_html = write_artifacts(
        envelope, runner.rubric, args.out_dir, remediation_templates=remediation,
    )
    rate, level = runner.summarize(envelope)

    artifacts_dict = {
        "readiness-report.json": str(report_json),
        "readiness-report.md": str(report_md),
        "readiness-actions.json": str(actions_json),
    }
    if dashboard_html:
        artifacts_dict["readiness-dashboard.html"] = str(dashboard_html)

    output = {
        "repoUrl": envelope.repoUrl,
        "rubricVersion": envelope.rubricVersion,
        "criteriaCount": len(envelope.report),
        "passRate": round(rate, 4),
        "level": level,
        "artifacts": artifacts_dict,
    }
    print(json.dumps(output, indent=2))
    return 0
```

**Step 3: Update existing artifact test**

In `tests/test_artifacts.py`, update `test_artifacts_writer_creates_three_outputs`:

```python
def test_artifacts_writer_creates_four_outputs(tmp_path, sample_repo) -> None:
    from agent_readiness.rubric import load_remediation_templates

    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    remediation = load_remediation_templates()
    report_json, report_md, actions_json, dashboard_html = write_artifacts(
        envelope, runner.rubric, out, remediation_templates=remediation,
    )
    assert (out / "readiness-report.json").exists()
    assert (out / "readiness-report.md").exists()
    assert (out / "readiness-actions.json").exists()
    assert (out / "readiness-dashboard.html").exists()
    assert dashboard_html is not None


def test_artifacts_writer_without_remediation_skips_dashboard(tmp_path, sample_repo) -> None:
    out = tmp_path / "out"
    runner = ReadinessRunner(repo_path=sample_repo, options=RunOptions(execute_commands=False))
    envelope = runner.evaluate()
    report_json, report_md, actions_json, dashboard_html = write_artifacts(
        envelope, runner.rubric, out,
    )
    assert (out / "readiness-report.json").exists()
    assert not (out / "readiness-dashboard.html").exists()
    assert dashboard_html is None
```

**Step 4: Update CLI test**

In `tests/test_cli.py`, update `test_cli_run_writes_outputs`:

```python
def test_cli_run_writes_dashboard(sample_repo, tmp_path) -> None:
    out = tmp_path / "out"
    code = main(["run", "--repo", str(sample_repo), "--out-dir", str(out), "--no-command-execution"])
    assert code == 0
    assert (out / "readiness-dashboard.html").exists()
```

**Step 5: Run all tests**

```bash
uv run python -m pytest -v
```

Expected: All tests pass (except `test_remediation_coverage` if Task 4 not yet complete).

**Step 6: Commit**

```bash
git add src/agent_readiness/artifacts.py src/agent_readiness/cli.py tests/test_artifacts.py tests/test_cli.py
git commit -m "feat: integrate HTML dashboard as 4th pipeline artifact"
```

---

### Task 8: Run Full Pipeline End-to-End

**Files:** None — validation only.

**Step 1: Run the full test suite**

```bash
uv run python -m pytest -v
```

Expected: All tests pass.

**Step 2: Run the CLI against this repo**

```bash
agent-readiness run --repo . --out-dir ./out --no-command-execution
```

Expected: JSON output includes `readiness-dashboard.html` in artifacts.

**Step 3: Verify the dashboard file**

```bash
ls -la out/readiness-dashboard.html
head -5 out/readiness-dashboard.html
```

Expected: File exists, starts with `<!DOCTYPE html>`.

**Step 4: Open in browser (manual verification)**

Open `out/readiness-dashboard.html` in a browser. Verify:
- Summary header shows pass rate and level
- Level breakdown chart renders
- Criteria table shows all 81 criteria with correct status
- Clicking a failing criterion opens the remediation panel
- "Copy to Clipboard" copies the full prompt
- Filters work (pass/fail/skip, level, scope)

**Step 5: Clean up output directory**

```bash
rm -rf out/
```

---

### Task 9: Final Cleanup and Commit

**Step 1: Run linter/formatter if configured**

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

**Step 2: Run full test suite one final time**

```bash
uv run python -m pytest -v
```

**Step 3: Final commit if any cleanup was needed**

```bash
git add -A
git commit -m "chore: final cleanup for HTML dashboard feature"
```
