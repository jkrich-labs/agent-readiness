---
signal_name: Type Checking
---

## Criterion-Specific Fix Guidance

- **TypeScript projects**: Ensure `tsconfig.json` exists at the app root with `"strict": true` in `compilerOptions`. If a `tsconfig.json` exists but `strict` is `false` or absent, add `"strict": true`. Enable at minimum `noImplicitAny`, `strictNullChecks`, and `strictFunctionTypes` if you cannot enable the full `strict` flag immediately.
- **Python projects**: Configure `mypy` by adding a `[tool.mypy]` section to `pyproject.toml` or creating a `mypy.ini` / `.mypy.ini` file. Set `python_version`, `warn_return_any = true`, and `disallow_untyped_defs = true` at minimum. Install mypy: `pip install mypy` or add it to dev dependencies.
- **Python alternative**: `pyright` can be configured via `pyrightconfig.json` with `"typeCheckingMode": "basic"` or `"strict"`. Install via `pip install pyright` or use the Pylance VS Code extension.
- Add type-check commands to project scripts: in `package.json` add `"typecheck": "tsc --noEmit"`, or in `pyproject.toml` add a mypy invocation to your test/lint scripts.
- Integrate type checking into CI: add a dedicated step in `.github/workflows/ci.yml` that runs `tsc --noEmit` or `mypy .` and fails the build on type errors.
- For gradual adoption in Python, start with `mypy --ignore-missing-imports` and a per-module override list, tightening over time.

## Criterion-Specific Exploration Steps

- Check for `tsconfig.json` at the app root and in subdirectories; inspect `compilerOptions.strict` value
- Check for `mypy.ini`, `.mypy.ini`, `setup.cfg` `[mypy]` section, or `pyproject.toml` `[tool.mypy]` section
- Check for `pyrightconfig.json` or `pyproject.toml` `[tool.pyright]` section
- Look at `package.json` `devDependencies` for `typescript` and scripts that run `tsc`
- Check CI workflows for type-checking steps (`tsc --noEmit`, `mypy`, `pyright`)

## Criterion-Specific Verification Steps

- **TypeScript**: Run `npx tsc --noEmit` and confirm it exits successfully (or with only pre-existing errors, not a config error)
- **Python**: Run `mypy .` or `mypy src/` and confirm it executes without configuration errors
- Verify the config file contains the strict settings: parse `tsconfig.json` and confirm `strict: true`, or parse `pyproject.toml` and confirm `[tool.mypy]` has `disallow_untyped_defs = true`
