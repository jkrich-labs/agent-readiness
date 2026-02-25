---
signal_name: Documentation Freshness
---

## Criterion-Specific Fix Guidance

- Update `README.md` to reflect the current state of the project: correct setup instructions, current dependencies, accurate build/test commands.
- If `AGENTS.md` or `CLAUDE.md` exists, review it for accuracy and update any stale references to files, commands, or architecture that have changed.
- If `CONTRIBUTING.md` exists, ensure it describes the current branching strategy, PR process, and coding standards.
- Add a date or "last reviewed" note at the bottom of key docs so staleness is visible.
- **Automation**: Add a CI job or scheduled GitHub Action that checks doc freshness. Example: a workflow that runs monthly and opens an issue if `README.md` has not been modified in 180 days.
- If docs are accurate but just have not been touched, make a meaningful update (even fixing a typo or improving a section) and commit to reset the freshness clock.
- Consider adding a `pre-commit` hook or CI check that flags when code changes affect documented commands or paths without corresponding doc updates.

## Criterion-Specific Exploration Steps

- Run `git log -1 --format="%ci" -- README.md` to check when README was last modified
- Similarly check `AGENTS.md`, `CLAUDE.md`, and `CONTRIBUTING.md` last-modified dates
- Compare documented commands (build, test, run) against actual `package.json` scripts or `pyproject.toml` to find drift
- Check if any referenced file paths in docs no longer exist

## Criterion-Specific Verification Steps

- Confirm at least one of `README.md`, `AGENTS.md`, or `CONTRIBUTING.md` was modified within the last 180 days using `git log -1 --format="%ci" -- <file>`
- Verify the content of the updated docs is substantive and accurate (not just a whitespace change)
