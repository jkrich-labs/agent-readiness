---
signal_name: AGENTS.md Validation
---

## Criterion-Specific Fix Guidance

- Add automated validation that `AGENTS.md` (or `CLAUDE.md`) stays consistent with the actual codebase.
- **CI-based approach**: Create a GitHub Actions workflow that parses `AGENTS.md` and verifies referenced file paths, commands, and directory structures still exist. Fail the workflow if any referenced paths are missing.
- **Pre-commit hook approach**: Add a custom `pre-commit` hook that checks `AGENTS.md` references on every commit. Use a script that extracts file paths and commands from the doc and validates them.
- **Example validation script** (`scripts/validate-agents-md.sh`):
  ```bash
  #!/bin/bash
  # Extract backtick-quoted file paths from AGENTS.md and verify they exist
  grep -oP '`[^`]*\.(py|ts|js|json|yml|yaml|toml|cfg)`' AGENTS.md | tr -d '`' | while read -r path; do
    [ -e "$path" ] || echo "ERROR: $path referenced in AGENTS.md does not exist"
  done
  ```
- **Doc-test approach**: If `AGENTS.md` contains shell commands, add a CI step that dry-runs or validates those commands (e.g., check that `make test` or `npm test` commands referenced in the doc are valid).
- For Python repos, consider `pytest`-based doc validation that imports and checks paths mentioned in `AGENTS.md`.
- Add the validation step to the main CI workflow so it runs on every PR, catching drift before merge.

## Criterion-Specific Exploration Steps

- Check if `AGENTS.md` or `CLAUDE.md` exists and what file paths, commands, or directory references it contains
- Look at `.github/workflows/` for any existing doc validation steps
- Check `.pre-commit-config.yaml` for custom hooks that might already validate docs
- Review `AGENTS.md` content to identify what kinds of references need validation (file paths, commands, URLs)

## Criterion-Specific Verification Steps

- Confirm a CI workflow or pre-commit hook exists that explicitly validates `AGENTS.md` content
- Intentionally break a reference in `AGENTS.md` (e.g., rename a referenced file path) and verify the validation catches it
- Run the CI workflow or pre-commit hook locally and confirm it passes on the current codebase
