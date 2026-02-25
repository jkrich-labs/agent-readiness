# Readiness Report Clone Design (Claude Code)

Date: 2026-02-25
Status: Approved
Owner: agent-readiness

## 1. Goals
- Build a local-only clone of Droid `/readiness-report` behavior for Claude Code.
- Preserve behavioral parity for scoring, criterion IDs, denominator semantics, and output interpretation.
- Provide better extensibility and reliability while keeping parity guarantees explicit.

## 2. Locked Decisions
- Parity target: behavioral parity (not wire/API parity).
- Integration target: CLI core plus Claude Code skill wrapper.
- Persistence: local-only; no Factory API integration.
- Rubric: fixed 81 criteria in v1.
- Outputs: JSON report + Markdown summary + JSON action plan.
- Check depth: deep checks for all 81 criteria in v1.
- Language support in v1: Python, TypeScript/JavaScript, Go, Rust.
- Non-applicable criteria: `numerator = null` and excluded from pass-rate denominator.
- Runtime verification: execute repo commands by default.

## 3. Rubric Source of Truth
Use a frozen local snapshot extracted from installed Droid/runtime artifacts.

Planned artifacts:
- `rubric/droid/v0.62.1/criteria_order.txt`
- `rubric/droid/v0.62.1/criteria_scope.json`
- `rubric/droid/v0.62.1/scoring_rules.json`
- `rubric/droid/v0.62.1/provenance.json`

Provenance must include:
- extraction timestamp
- source artifact paths
- content hashes
- droid version used for extraction

## 4. Architecture
Adopt a hybrid architecture: strict core + domain check packs.

### 4.1 Core Engine (parity-critical)
- Discovery: repo root, apps, language detection.
- Contract: fixed 81-key schema and scope constraints.
- Execution orchestration: deterministic criterion order.
- Scoring: pass-rate and level mapping.
- Artifact writing: JSON, Markdown, action plan.

### 4.2 Domain Check Packs
Grouped evaluator modules (style, build, testing, docs, dev environment, observability, security, process/product).

Each evaluator returns normalized result:
- `criterion_id`
- `numerator`
- `denominator`
- `rationale`
- `evidence[]`
- `app_scope` (`repo` or app-path)

## 5. Data Contract
Runtime report schema (local):
- `repoUrl`
- `apps`
- `report`
- git/runtime metadata

Criterion value shape:
- `numerator: int | null`
- `denominator: int >= 1`
- `rationale: str`
- `evidence: list`

Validation rules:
- exactly 81 criterion keys
- repository-scope denominator is always 1
- application-scope denominator is app count
- numerator bounds: `0 <= numerator <= denominator` when not null

## 6. Scoring Model
- Exclude skipped criteria (`numerator == null`) from pass-rate denominator.
- Pass-rate formula:
  - average of `(numerator / denominator)` over non-skipped criteria
- Level bands:
  - Level 1: [0.0, 0.2)
  - Level 2: [0.2, 0.4)
  - Level 3: [0.4, 0.6)
  - Level 4: [0.6, 0.8)
  - Level 5: [0.8, 1.0]

## 7. Error Handling and Reliability
Defined errors:
- `RubricMismatchError`
- `DiscoveryError`
- `CheckExecutionError`
- `ValidationError`
- `ArtifactWriteError`

Policy:
- applicable check execution failure -> fail criterion (`0/denominator`) with explicit evidence
- non-applicable only -> `null` numerator
- per-check timeout + global timeout
- deterministic ordering for apps and criteria

## 8. CLI and Skill UX
CLI commands:
- `agent-readiness run [--repo PATH] [--out-dir PATH]`
- `agent-readiness explain <criterion-id>`
- `agent-readiness self-check`

Outputs:
- `readiness-report.json`
- `readiness-report.md`
- `readiness-actions.json`

Claude Code skill:
- wraps CLI execution
- summarizes failures and actions
- supports focused modes (category, failed-only)

## 9. Test Strategy
- Rubric integrity tests (count/order/scope/hash).
- Unit tests per criterion evaluator (including error and timeout paths).
- Language-specific parser tests for command outputs.
- Golden end-to-end fixture repos with snapshot assertions for all artifacts.
- Coverage gate: every frozen criterion must map to exactly one evaluator.

## 10. High-Level Delivery Sequence
1. Freeze rubric snapshot from local Droid evidence.
2. Implement strict core (contract, scoring, validation).
3. Implement discovery and app/language modeling.
4. Implement all 81 deep evaluators.
5. Implement artifact renderers (JSON/MD/actions).
6. Build CLI interface.
7. Build Claude Code skill wrapper.
8. Add full automated test suite and golden fixtures.
9. Run parity validation against known historical behavior.

## 11. Explicit Non-Goals (v1)
- Any Factory API write/read integration.
- User-configurable rubric changes.
- Partial rubric execution as default mode.
