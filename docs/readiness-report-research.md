# `/readiness-report` Research Notes (Droid)

## Scope
This document captures how Droid's `/readiness-report` behavior works in practice based on observed runtime logs, session traces, and public Factory docs.

## Evidence Summary

### 1) Command surface
- Public doc: `/readiness-report` is a CLI slash command under Agent Readiness.
- Prerequisite: enable in `/settings -> Experimental -> Readiness Report`.
- Source: `https://docs.factory.ai/cli/features/readiness-report`

### 2) Runtime behavior in real session
- Successful run session: `~/.factory/sessions/-home-johnr-dev-repos-pinion/632a3d8e-7627-40f4-86c0-7a0e31fe4e63.jsonl`
- Observed tool call: `store_agent_readiness_report`
- Observed result: success with report id `ffe9f1bb-c655-4644-8c86-fab7646cf897`

### 3) Persistence path
- CLI log evidence shows submission to:
  - `POST https://app.factory.ai/api/organization/agent-readiness-reports`
- Read API doc for historical retrieval:
  - `GET /api/organization/maturity-level-reports`
- Source: `https://docs.factory.ai/reference/readiness-reports-api`

### 4) Schema/contract constraints
- Report payload includes:
  - `repoUrl`, `apps`, `report`, plus git/model metadata fields
- `report` requires criterion entries shaped as:
  - `{ "numerator": int|null, "denominator": int>=1, "rationale": string }`
- In successful run, report contained exactly **81 criteria**.
- Scope split observed:
  - **43 repository-scope** criteria with denominator `1`
  - **38 application-scope** criteria with denominator `N apps`

### 5) Known validation failure mode
- Historical failed run (`37ffcbfc-e632-49cf-ad09-ccc27ec9660c`) returned 400:
  - `apps is required and must be an object with app paths as keys and description objects as values`
- Implication: server-side schema checks are strict; client preflight validation is required.

## Scoring Model (Observed)
- Pass rate is computed as average of per-criterion ratios over non-skipped criteria:
  - `avg(numerator/denominator)` where `numerator != null`
- Level mapping:
  - Level 1: `[0.0, 0.2)`
  - Level 2: `[0.2, 0.4)`
  - Level 3: `[0.4, 0.6)`
  - Level 4: `[0.6, 0.8)`
  - Level 5: `[0.8, 1.0]`

## Recreate Plan

1. **Evaluator contract layer**
   - Freeze criterion inventory (81 IDs) and scope mapping (43 repo / 38 app).
   - Enforce denominator semantics by scope before network submission.

2. **Repository audit layer**
   - App discovery (`apps` object generation)
   - Criterion handlers by category (lint, test, observability, process, security)
   - Deterministic rationale text generation

3. **Validation + scoring layer**
   - Verify exact key set + unique IDs
   - Validate numeric bounds and skip/null rules
   - Compute pass rate and maturity level

4. **Persistence layer**
   - POST to agent-readiness-reports
   - GET maturity-level-reports for history/trends

5. **Presentation layer**
   - Human-readable summary
   - Action items ordered by impact and prerequisite dependencies

## Improvement Opportunities
- Add local schema preflight to prevent avoidable 400s.
- Add rubric versioning (`rubricVersion`, `schemaVersion`).
- Add incremental mode (re-evaluate selected criteria/categories only).
- Add remediation mode for selected failed criteria.
- Add deterministic test harness with golden repos and expected scores.

## Skeleton in this repository
- `src/agent_readiness/criteria.py` — criterion inventory + count checks
- `src/agent_readiness/validator.py` — strict envelope validation
- `src/agent_readiness/scoring.py` — pass-rate and level mapping
- `src/agent_readiness/persister.py` — local-only report persistence
- `src/agent_readiness/runner.py` — orchestration skeleton
- `src/agent_readiness/cli.py` — minimal CLI entrypoint

## Local Rubric Freeze (v0.62.1)
- Extraction script: `scripts/extract_droid_rubric.py`
- Extraction source: local Factory session prompt body that contains Droid's exact 81-ID list and scope definitions.
- Frozen artifacts:
  - `rubric/droid/v0.62.1/criteria_order.txt`
  - `rubric/droid/v0.62.1/criteria_scope.json`
  - `rubric/droid/v0.62.1/scoring_rules.json`
  - `rubric/droid/v0.62.1/provenance.json`
- Provenance records droid version, source path, and artifact hashes.
