---
signal_name: Strict Typing
---

## Criterion-Specific Fix Guidance

- **TypeScript projects**: Ensure `tsconfig.json` has `"strict": true` in `compilerOptions`. This enables all strict type-checking options including `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `noImplicitThis`, `useUnknownInCatchVariables`, and `alwaysStrict`. Do not use partial strict flags as a substitute for the full `strict` flag.
- **Python projects**: Configure mypy in strict mode by adding `strict = true` under `[tool.mypy]` in `pyproject.toml`. This enables `disallow_untyped_defs`, `disallow_any_generics`, `warn_return_any`, `no_implicit_optional`, and more. Alternatively, enable these flags individually if full strict mode causes too many initial errors.
- **Rust and Go projects**: These languages are typed by default. Rust enforces strict typing at compile time. Go enforces static typing. This criterion is automatically satisfied for these languages; no configuration is needed.
- For gradual migration to strict typing in TypeScript, use `// @ts-expect-error` annotations on specific lines rather than disabling strict mode. Track these annotations and reduce them over time.
- For gradual migration in Python, use per-module mypy overrides in `pyproject.toml`: `[[tool.mypy.overrides]]` with `module = "legacy_module.*"` and `disallow_untyped_defs = false`, tightening module by module.
- This criterion is skippable: if the app language does not support configurable strict typing (e.g., plain JavaScript without TypeScript), it will be skipped.

## Criterion-Specific Exploration Steps

- Check `tsconfig.json` for `"strict": true` vs individual strict flags
- Check `pyproject.toml` `[tool.mypy]` for `strict = true` or individual strict flags
- Check `mypy.ini` or `setup.cfg` `[mypy]` section for strict settings
- Identify the app language: Rust and Go satisfy this automatically
- Look for `// @ts-ignore` or `# type: ignore` comments that may indicate typing workarounds
- Check if `tsconfig.json` has `"strict": false` explicitly set (which overrides individual strict flags)

## Criterion-Specific Verification Steps

- **TypeScript**: Parse `tsconfig.json` and confirm `compilerOptions.strict === true` (not just individual flags)
- **Python**: Confirm `pyproject.toml` `[tool.mypy]` contains `strict = true`, or that all key strict flags are individually enabled
- **Rust/Go**: Confirm the language is Rust or Go (no config needed)
- Run `tsc --noEmit` or `mypy --strict .` and verify the command executes without configuration errors
