---
signal_name: Pre-Commit Hooks
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Install Husky (`npm install -D husky`) and initialize it (`npx husky init`). This creates a `.husky/` directory. Add a `pre-commit` hook file at `.husky/pre-commit` that runs linting and formatting: `npx lint-staged` or `npx eslint . && npx prettier --check .`.
- **Pair Husky with lint-staged**: Install `lint-staged` (`npm install -D lint-staged`) and add config to `package.json`: `"lint-staged": { "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"], "*.{json,md}": ["prettier --write"] }`. Add `npx lint-staged` to the `.husky/pre-commit` hook.
- **Python projects**: Install `pre-commit` (`pip install pre-commit`) and create `.pre-commit-config.yaml` at the repo root. Add hooks for `ruff` (linting and formatting) or `black` and `flake8`. Minimal config should include repos for `pre-commit-hooks` (trailing whitespace, end-of-file-fixer), `ruff-pre-commit`, and optionally `mypy`.
- Run `pre-commit install` to activate the hooks (or document this in the README/CONTRIBUTING guide).
- Add `pre-commit run --all-files` to CI to ensure hooks pass even if developers skip them locally.
- Example `.pre-commit-config.yaml` repos entry for ruff: `- repo: https://github.com/astral-sh/ruff-pre-commit, rev: v0.8.0, hooks: [{id: ruff, args: [--fix]}, {id: ruff-format}]`.

## Criterion-Specific Exploration Steps

- Check for `.husky/` directory and its contents (especially `pre-commit` hook file)
- Check for `.pre-commit-config.yaml` at the repo root
- Check `package.json` for `husky` and `lint-staged` in `devDependencies`
- Check `package.json` for a `prepare` script that runs `husky install` or `husky`
- Look for `.lintstagedrc`, `.lintstagedrc.json`, or `lint-staged` key in `package.json`
- Check if `pre-commit` is in Python dev dependencies

## Criterion-Specific Verification Steps

- **Husky**: Confirm `.husky/pre-commit` exists and contains executable commands (not just comments)
- **pre-commit**: Run `pre-commit run --all-files` and confirm hooks execute (even if some fail on existing code, the framework itself should work)
- Verify that the hooks include linting or formatting tools (ruff, black, eslint, prettier) rather than being empty stubs
- Check that `package.json` has a `prepare` script for Husky or that `.pre-commit-config.yaml` references real hook repos
