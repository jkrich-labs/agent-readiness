---
signal_name: Code Modularization
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Install `eslint-plugin-boundaries` (`npm install -D eslint-plugin-boundaries`) and configure module boundary rules in your ESLint config. Define element types (e.g., `feature`, `shared`, `core`) and specify which types can import from which. Example: features cannot import from other features, only from shared/core. Alternatively, use `eslint-plugin-import` with `no-restricted-paths` to enforce boundaries.
- **Python projects**: Install `import-linter` (`pip install import-linter`) and add `[tool.importlinter]` configuration to `pyproject.toml`. Define contracts such as `type = "layers"` with `layers = ["api", "service", "domain", "infrastructure"]` to enforce a layered architecture where lower layers cannot import from higher layers.
- **Go projects**: Use the `internal/` package convention to enforce module boundaries. Code in `internal/` can only be imported by code in the parent directory tree. Use `go vet` and `staticcheck` to verify import rules.
- **Java projects**: Use ArchUnit to write architecture tests that enforce module boundaries. Create tests like `noClasses().that().resideInAPackage("..domain..").should().dependOnClassesThat().resideInAPackage("..infrastructure..")`.
- This criterion is skippable: if the project is small or single-module, it may not be applicable.
- Add module boundary checks to CI so violations are caught before merging.

## Criterion-Specific Exploration Steps

- Check ESLint config for `eslint-plugin-boundaries` or `eslint-plugin-import` with `no-restricted-paths`
- Check `package.json` for `eslint-plugin-boundaries` in `devDependencies`
- Check `pyproject.toml` for `[tool.importlinter]` section
- Check Python dev dependencies for `import-linter`
- Look for Go `internal/` directories indicating boundary enforcement
- Check for ArchUnit test files in Java projects (`**/ArchitectureTest.java`, `**/ArchTest.java`)
- Look at the project structure to determine if it has clear module/package boundaries

## Criterion-Specific Verification Steps

- **TypeScript/JavaScript**: Run ESLint and confirm `boundaries/*` rules are active and produce results (not unknown-rule errors)
- **Python**: Run `lint-imports` and confirm it evaluates the configured contracts
- **Go**: Verify `internal/` directories exist and imports are correctly scoped
- Verify the module boundary config reflects the actual project architecture (not a generic template)
