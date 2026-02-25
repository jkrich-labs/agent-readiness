---
signal_name: Naming Consistency
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Add the `@typescript-eslint/naming-convention` rule to your ESLint config. Configure it to enforce camelCase for variables and functions, PascalCase for classes and type aliases, and UPPER_CASE for constants. Example: `"@typescript-eslint/naming-convention": ["error", { "selector": "variable", "format": ["camelCase", "UPPER_CASE"] }, { "selector": "typeLike", "format": ["PascalCase"] }]`.
- **Python projects**: Enable pylint naming-style checks by adding `[tool.pylint."messages control"]` to `pyproject.toml` or using `ruff` with the `N` (pep8-naming) rule set enabled. Ruff config: add `"N"` to the `select` list in `[tool.ruff.lint]`. This enforces PEP 8 naming: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- **Go projects**: Run `golint` or `staticcheck` which enforces Go naming conventions (MixedCaps, no underscores in exported names). Add to CI or pre-commit hooks.
- **Documentation alternative**: If automated enforcement is not feasible, create a `CONVENTIONS.md` or a naming section in `CONTRIBUTING.md` that explicitly documents the naming rules for the project.
- Add naming convention checks to CI so violations fail the build.

## Criterion-Specific Exploration Steps

- Check ESLint config for `@typescript-eslint/naming-convention` rule or `eslint-plugin-unicorn` naming rules
- Check `pyproject.toml` for ruff `N` rules or pylint naming-style configuration
- Check for `CONVENTIONS.md`, `CONTRIBUTING.md`, or `STYLE_GUIDE.md` that documents naming rules
- Look at `.golangci.yml` for `revive` or `stylecheck` linter configuration (Go)
- Check `setup.cfg` or `.pylintrc` for `[FORMAT]` naming-style settings

## Criterion-Specific Verification Steps

- **TypeScript**: Run `npx eslint . --rule '{"@typescript-eslint/naming-convention": "error"}'` and verify the rule is active (produces results, not an unknown-rule error)
- **Python**: Run `ruff check . --select N` and confirm naming rules are evaluated
- **Documentation**: Verify that a naming conventions document exists and contains specific rules (not just a vague mention of "follow conventions")
- Check that CI pipeline includes the naming convention checks
