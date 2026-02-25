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
