# Agent Readiness

Local-only clone of Droid `/readiness-report` with a frozen Droid `v0.62.1` rubric snapshot, Claude Code skill wrapper, and artifact generation.

## Rubric Snapshot

The rubric is frozen under:

- `rubric/droid/v0.62.1/criteria_order.txt`
- `rubric/droid/v0.62.1/criteria_scope.json`
- `rubric/droid/v0.62.1/scoring_rules.json`
- `rubric/droid/v0.62.1/provenance.json`

Regenerate from local Droid session evidence:

```bash
python3 scripts/extract_droid_rubric.py
```

## Install

```bash
python3 -m pip install -e '.[dev]'
```

## CLI

Run full evaluation and write local artifacts:

```bash
agent-readiness run --repo . --out-dir ./out
```

Explain a criterion:

```bash
agent-readiness explain lint_config
```

Validate local installation and registry coverage:

```bash
agent-readiness self-check
```

## Outputs

`agent-readiness run` writes:

- `readiness-report.json`
- `readiness-report.md`
- `readiness-actions.json`

## Notes

- This implementation is local-only and does not use Factory APIs.
- Non-applicable skippable criteria use `numerator: null`.
- Pass rate excludes skipped criteria from the denominator.
