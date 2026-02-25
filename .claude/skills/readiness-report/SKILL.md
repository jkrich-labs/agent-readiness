---
name: readiness-report
description: Run local readiness CLI and summarize failures for Claude Code users.
---

# Readiness Report Skill

## Purpose

Run the local `agent-readiness` CLI against the current repository and summarize failed criteria with actionable next steps.

## Usage

1. Execute:

```bash
agent-readiness run --repo . --out-dir ./.readiness
```

2. Read outputs:
- `.readiness/readiness-report.json`
- `.readiness/readiness-report.md`
- `.readiness/readiness-actions.json`

3. Summarize:
- current pass rate and level
- top failing criteria by level
- top 3 actions from `readiness-actions.json`

## Focus Modes

- Failed-only: summarize only failed and skipped criteria.
- Category focus: filter by criterion prefix or known category mapping.

## Guardrails

- Do not call external Factory APIs.
- Keep rubric fixed to local `v0.62.1` snapshot unless explicitly changed.
