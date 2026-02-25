---
signal_name: Code Formatter
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Install Prettier (`npm install -D prettier`) and create a `.prettierrc` or `.prettierrc.json` config file. Minimal config: `{ "semi": true, "singleQuote": true, "trailingComma": "es5" }`. Add a format script to `package.json`: `"format": "prettier --write ."` and a check script: `"format:check": "prettier --check ."`.
- **Python projects**: Configure Black by adding `[tool.black]` to `pyproject.toml` with settings like `line-length = 88` (default) and `target-version`. Install via `pip install black` or add to dev dependencies. Alternative: `ruff format` can replace Black with `[tool.ruff.format]` configuration.
- Create a `.prettierignore` file to exclude `node_modules/`, `dist/`, `build/`, and generated files.
- For Python, ensure `ruff` or `black` is listed in dev dependencies (`pyproject.toml` `[project.optional-dependencies]` or `requirements-dev.txt`).
- Integrate formatting checks into CI: add a step that runs `prettier --check .` or `black --check .` to catch unformatted code.
- Consider adding format-on-save configuration in `.vscode/settings.json`: `"editor.formatOnSave": true` with the appropriate formatter extension.

## Criterion-Specific Exploration Steps

- Check for `.prettierrc`, `.prettierrc.json`, `.prettierrc.yml`, `.prettierrc.js`, or `prettier.config.js`
- Check for `[tool.black]` in `pyproject.toml` or `[tool.ruff.format]` section
- Check `package.json` for `prettier` in `devDependencies` and format-related scripts
- Look for `.editorconfig` which may indicate some formatting standards are in place
- Check CI workflows for formatting steps

## Criterion-Specific Verification Steps

- **TypeScript/JavaScript**: Run `npx prettier --check .` and confirm it exits successfully (all files formatted)
- **Python**: Run `black --check .` or `ruff format --check .` and confirm it reports no changes needed
- Verify the config file exists and is not empty or trivially disabled
