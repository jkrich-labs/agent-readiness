# Readiness Report Clone Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local-only, Claude Code-ready readiness report system with fixed Droid-compatible 81-criterion behavioral parity.

**Architecture:** Keep a strict parity core (rubric, discovery, validation, scoring, orchestration) and layered criterion check packs for Python/TS/Go/Rust. Every criterion produces deterministic `{numerator, denominator, rationale, evidence}` output and local artifacts (`json`, `md`, `actions`). CLI is the source of truth and a Claude skill wraps CLI execution.

**Tech Stack:** Python 3.11+, stdlib + `requests`, pytest, dataclasses, argparse.

---

### Task 1: Test Harness and Plan Scaffolding

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/conftest.py`
- Create: `tests/test_plan_smoke.py`

**Step 1: Write the failing test**

```python
def test_pytest_harness_is_active() -> None:
    assert False, "replace with harness assertion"
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_plan_smoke.py -v`
Expected: FAIL with assertion message.

**Step 3: Write minimal implementation**

```toml
[project.optional-dependencies]
dev = ["pytest>=8,<9"]
```

```python

def test_pytest_harness_is_active() -> None:
    assert True
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_plan_smoke.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add pyproject.toml tests/conftest.py tests/test_plan_smoke.py
git commit -m "test: add pytest harness for readiness implementation"
```

### Task 2: Freeze Rubric Snapshot from Local Droid Evidence

**Files:**
- Create: `scripts/extract_droid_rubric.py`
- Create: `rubric/droid/v0.62.1/criteria_order.txt`
- Create: `rubric/droid/v0.62.1/criteria_scope.json`
- Create: `rubric/droid/v0.62.1/scoring_rules.json`
- Create: `rubric/droid/v0.62.1/provenance.json`
- Test: `tests/test_rubric_snapshot.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_frozen_rubric_has_exactly_81_criteria() -> None:
    lines = Path("rubric/droid/v0.62.1/criteria_order.txt").read_text().splitlines()
    assert len(lines) == 81
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_rubric_snapshot.py -v`
Expected: FAIL because rubric files do not exist yet.

**Step 3: Write minimal implementation**

```python
# scripts/extract_droid_rubric.py (core output sketch)
criteria = payload["report"].keys()
Path("rubric/droid/v0.62.1/criteria_order.txt").write_text("\n".join(criteria) + "\n")
```

**Step 4: Run test to verify it passes**

Run: `python3 scripts/extract_droid_rubric.py && python3 -m pytest tests/test_rubric_snapshot.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add scripts/extract_droid_rubric.py rubric/droid/v0.62.1 tests/test_rubric_snapshot.py
git commit -m "feat: freeze droid rubric snapshot v0.62.1"
```

### Task 3: Rubric Loader and Integrity Guard

**Files:**
- Create: `src/agent_readiness/rubric.py`
- Modify: `src/agent_readiness/criteria.py`
- Test: `tests/test_rubric_loader.py`

**Step 1: Write the failing test**

```python
from agent_readiness.rubric import load_frozen_rubric


def test_rubric_loader_returns_81_unique_criteria() -> None:
    rubric = load_frozen_rubric("v0.62.1")
    assert len(rubric.criteria_order) == 81
    assert len(set(rubric.criteria_order)) == 81
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_rubric_loader.py -v`
Expected: FAIL (module/function missing).

**Step 3: Write minimal implementation**

```python
@dataclass(frozen=True)
class FrozenRubric:
    version: str
    criteria_order: tuple[str, ...]
    repository_scope: frozenset[str]
    application_scope: frozenset[str]
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_rubric_loader.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/rubric.py src/agent_readiness/criteria.py tests/test_rubric_loader.py
git commit -m "feat: add frozen rubric loader and integrity guards"
```

### Task 4: Strict Report Contract and Validation

**Files:**
- Modify: `src/agent_readiness/models.py`
- Modify: `src/agent_readiness/validator.py`
- Create: `tests/test_validator_contract.py`

**Step 1: Write the failing test**

```python
def test_validator_rejects_missing_criterion_key() -> None:
    envelope = make_valid_envelope()
    envelope.report.pop("lint_config")
    with pytest.raises(ValueError):
        validate_report_shape(envelope)
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_validator_contract.py::test_validator_rejects_missing_criterion_key -v`
Expected: FAIL before validator is updated.

**Step 3: Write minimal implementation**

```python
missing = expected_keys - report_keys
extra = report_keys - expected_keys
if missing or extra:
    raise ValueError(...)
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_validator_contract.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/models.py src/agent_readiness/validator.py tests/test_validator_contract.py
git commit -m "feat: enforce strict report contract validation"
```

### Task 5: Scoring Engine Parity Tests

**Files:**
- Modify: `src/agent_readiness/scoring.py`
- Modify: `tests/test_scoring.py`

**Step 1: Write the failing test**

```python
def test_pass_rate_excludes_skipped_criteria() -> None:
    report = {
        "a": CriterionEvaluation(1, 1, "ok"),
        "b": CriterionEvaluation(None, 2, "skip"),
        "c": CriterionEvaluation(0, 1, "fail"),
    }
    assert pass_rate(report) == 0.5
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_scoring.py::test_pass_rate_excludes_skipped_criteria -v`
Expected: FAIL if behavior drifts.

**Step 3: Write minimal implementation**

```python
non_skipped = [v for v in report.values() if v.numerator is not None]
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_scoring.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/scoring.py tests/test_scoring.py
git commit -m "feat: lock scoring parity semantics"
```

### Task 6: Discovery Engine (Repo Root, Apps, Languages)

**Files:**
- Create: `src/agent_readiness/discovery.py`
- Create: `tests/test_discovery.py`

**Step 1: Write the failing test**

```python
def test_discovery_detects_backend_and_frontend_apps(tmp_path: Path) -> None:
    # create minimal backend/frontend markers
    result = discover_repository(tmp_path)
    assert "backend" in result.apps
    assert "frontend" in result.apps
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_discovery.py -v`
Expected: FAIL (module missing).

**Step 3: Write minimal implementation**

```python
if (root / "backend" / "pyproject.toml").exists(): apps["backend"] = ...
if (root / "frontend" / "package.json").exists(): apps["frontend"] = ...
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_discovery.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/discovery.py tests/test_discovery.py
git commit -m "feat: add deterministic app and language discovery"
```

### Task 7: Command Runner and Evidence Capture

**Files:**
- Create: `src/agent_readiness/command_runner.py`
- Create: `tests/test_command_runner.py`

**Step 1: Write the failing test**

```python
def test_command_runner_captures_exit_code_and_output() -> None:
    result = run_command(["bash", "-lc", "echo ok"])
    assert result.exit_code == 0
    assert "ok" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_command_runner.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
return CommandResult(exit_code=cp.returncode, stdout=cp.stdout, stderr=cp.stderr)
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_command_runner.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/command_runner.py tests/test_command_runner.py
git commit -m "feat: add command execution and evidence capture"
```

### Task 8: Evaluator Interface and Registry Coverage Guard

**Files:**
- Create: `src/agent_readiness/evaluators/base.py`
- Create: `src/agent_readiness/evaluators/registry.py`
- Create: `tests/test_registry_coverage.py`

**Step 1: Write the failing test**

```python
def test_registry_has_exact_coverage_for_frozen_rubric() -> None:
    rubric = load_frozen_rubric("v0.62.1")
    registered = set(build_registry().keys())
    assert registered == set(rubric.criteria_order)
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_registry_coverage.py -v`
Expected: FAIL with missing criteria.

**Step 3: Write minimal implementation**

```python
class CriterionEvaluator(Protocol):
    def evaluate(self, ctx: EvaluationContext) -> CriterionEvaluation: ...
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_registry_coverage.py -v`
Expected: PASS only when all 81 are wired.

**Step 5: Commit**

```bash
git add src/agent_readiness/evaluators tests/test_registry_coverage.py
git commit -m "feat: add evaluator registry with full rubric coverage guard"
```

### Task 9: Implement Style + Build Criterion Pack

**Files:**
- Create: `src/agent_readiness/evaluators/style_build.py`
- Create: `tests/test_style_build_pack.py`
- Modify: `src/agent_readiness/evaluators/registry.py`

**Step 1: Write the failing test**

```python
def test_lint_config_passes_when_lint_tooling_present() -> None:
    result = eval_lint_config(ctx_with_python_and_ts_linters())
    assert result.numerator == result.denominator
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_style_build_pack.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
def eval_lint_config(ctx):
    ok = ctx.has_any(["ruff", "eslint", "biome"])
    return score_app_scope(ok, ctx.app_count, "...rationale...")
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_style_build_pack.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/evaluators/style_build.py src/agent_readiness/evaluators/registry.py tests/test_style_build_pack.py
git commit -m "feat: implement style and build criterion evaluators"
```

### Task 10: Implement Testing + Documentation Criterion Pack

**Files:**
- Create: `src/agent_readiness/evaluators/testing_docs.py`
- Create: `tests/test_testing_docs_pack.py`
- Modify: `src/agent_readiness/evaluators/registry.py`

**Step 1: Write the failing test**

```python
def test_unit_tests_exist_counts_per_app() -> None:
    result = eval_unit_tests_exist(ctx_with_backend_and_frontend_tests())
    assert result.numerator == 2
    assert result.denominator == 2
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_testing_docs_pack.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
def eval_unit_tests_exist(ctx):
    num = int(ctx.backend_has_tests) + int(ctx.frontend_has_tests)
    return CriterionEvaluation(num, ctx.app_count, "...")
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_testing_docs_pack.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/evaluators/testing_docs.py src/agent_readiness/evaluators/registry.py tests/test_testing_docs_pack.py
git commit -m "feat: implement testing and documentation criterion evaluators"
```

### Task 11: Implement Dev Environment + Observability Criterion Pack

**Files:**
- Create: `src/agent_readiness/evaluators/dev_observability.py`
- Create: `tests/test_dev_observability_pack.py`
- Modify: `src/agent_readiness/evaluators/registry.py`

**Step 1: Write the failing test**

```python
def test_health_checks_partially_pass_for_backend_only() -> None:
    result = eval_health_checks(ctx_backend_has_health_frontend_not_applicable())
    assert result.numerator == 1
    assert result.denominator == 2
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_dev_observability_pack.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
def eval_health_checks(ctx):
    # backend health endpoint + frontend service checks
    ...
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_dev_observability_pack.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/evaluators/dev_observability.py src/agent_readiness/evaluators/registry.py tests/test_dev_observability_pack.py
git commit -m "feat: implement dev environment and observability evaluators"
```

### Task 12: Implement Security + Process/Product Criterion Pack

**Files:**
- Create: `src/agent_readiness/evaluators/security_process.py`
- Create: `tests/test_security_process_pack.py`
- Modify: `src/agent_readiness/evaluators/registry.py`

**Step 1: Write the failing test**

```python
def test_branch_protection_fails_when_no_rules_detected() -> None:
    result = eval_branch_protection(ctx_without_branch_rules())
    assert result.numerator == 0
    assert result.denominator == 1
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_security_process_pack.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
def eval_branch_protection(ctx):
    protected = ctx.git_branch_protection_enabled
    return CriterionEvaluation(int(protected), 1, "...")
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_security_process_pack.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/evaluators/security_process.py src/agent_readiness/evaluators/registry.py tests/test_security_process_pack.py
git commit -m "feat: implement security and process criterion evaluators"
```

### Task 13: Orchestration Runner Using Full Registry

**Files:**
- Modify: `src/agent_readiness/runner.py`
- Create: `tests/test_runner_orchestration.py`

**Step 1: Write the failing test**

```python
def test_runner_produces_81_criterion_report() -> None:
    report = ReadinessRunner(...).evaluate()
    assert len(report.report) == 81
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_runner_orchestration.py -v`
Expected: FAIL while runner still uses skeleton defaults.

**Step 3: Write minimal implementation**

```python
registry = build_registry()
for criterion_id in rubric.criteria_order:
    report[criterion_id] = registry[criterion_id].evaluate(ctx)
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_runner_orchestration.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/runner.py tests/test_runner_orchestration.py
git commit -m "feat: wire runner to full 81-criterion evaluator registry"
```

### Task 14: Artifact Writers (JSON + Markdown + Actions)

**Files:**
- Create: `src/agent_readiness/artifacts.py`
- Create: `tests/test_artifacts.py`

**Step 1: Write the failing test**

```python
def test_artifacts_writer_creates_three_outputs(tmp_path: Path) -> None:
    write_artifacts(report, tmp_path)
    assert (tmp_path / "readiness-report.json").exists()
    assert (tmp_path / "readiness-report.md").exists()
    assert (tmp_path / "readiness-actions.json").exists()
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_artifacts.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```python
(out / "readiness-report.json").write_text(json_text)
(out / "readiness-report.md").write_text(markdown_text)
(out / "readiness-actions.json").write_text(actions_text)
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_artifacts.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/artifacts.py tests/test_artifacts.py
git commit -m "feat: generate readiness json markdown and actions artifacts"
```

### Task 15: CLI Commands (`run`, `explain`, `self-check`)

**Files:**
- Modify: `src/agent_readiness/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
def test_cli_self_check_returns_zero() -> None:
    code = main(["self-check"])
    assert code == 0
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_cli.py::test_cli_self_check_returns_zero -v`
Expected: FAIL (subcommand missing).

**Step 3: Write minimal implementation**

```python
sub = parser.add_subparsers(dest="cmd", required=True)
sub.add_parser("self-check")
sub.add_parser("run")
sub.add_parser("explain")
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_cli.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/agent_readiness/cli.py tests/test_cli.py
git commit -m "feat: add readiness cli run explain and self-check commands"
```

### Task 16: Claude Skill Wrapper

**Files:**
- Create: `.claude/skills/readiness-report/SKILL.md`
- Create: `.claude/skills/readiness-report/templates/summary.md`
- Create: `tests/test_skill_presence.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_skill_wrapper_exists() -> None:
    assert Path(".claude/skills/readiness-report/SKILL.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_skill_presence.py -v`
Expected: FAIL.

**Step 3: Write minimal implementation**

```markdown
name: readiness-report
description: Run local readiness CLI and summarize failures for Claude Code users.
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_skill_presence.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add .claude/skills/readiness-report tests/test_skill_presence.py
git commit -m "feat: add claude skill wrapper for readiness cli"
```

### Task 17: Full Regression and Golden Fixture Verification

**Files:**
- Create: `tests/golden/expected/README.md`
- Create: `tests/test_end_to_end_golden.py`

**Step 1: Write the failing test**

```python
def test_end_to_end_output_matches_golden(tmp_path: Path) -> None:
    run_cli_on_fixture("polyglot_repo", tmp_path)
    assert (tmp_path / "readiness-report.json").read_text() == load_golden("readiness-report.json")
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_end_to_end_golden.py -v`
Expected: FAIL until fixtures/golden outputs are generated.

**Step 3: Write minimal implementation**

```python
# generate fixture outputs once and commit as golden baseline
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest -v`
Expected: PASS for full suite.

**Step 5: Commit**

```bash
git add tests/golden tests/test_end_to_end_golden.py
git commit -m "test: add end-to-end golden regression coverage"
```

### Task 18: Final Verification and Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/readiness-report-research.md`

**Step 1: Write the failing test**

```python
def test_readme_documents_cli_commands() -> None:
    text = Path("README.md").read_text()
    assert "agent-readiness run" in text
    assert "agent-readiness self-check" in text
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_plan_smoke.py tests/test_readme_commands.py -v`
Expected: FAIL if docs not updated.

**Step 3: Write minimal implementation**

```markdown
## CLI
- agent-readiness run
- agent-readiness explain <criterion-id>
- agent-readiness self-check
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest -v`
Expected: PASS for entire suite.

**Step 5: Commit**

```bash
git add README.md docs/readiness-report-research.md tests
git commit -m "docs: add usage and verification guidance for readiness clone"
```

---

## Execution Notes
- TDD required for every task (red -> green -> commit).
- Keep commits task-scoped and small.
- Use `@superpowers:verification-before-completion` before declaring done.
- For execution in this session use `@superpowers:subagent-driven-development`.
- For separate execution session use `@superpowers:executing-plans`.
