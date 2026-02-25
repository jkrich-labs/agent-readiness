---
signal_name: Cyclomatic Complexity
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Enable the ESLint `complexity` rule in your config: `"complexity": ["warn", { "max": 10 }]`. This warns on functions exceeding the threshold. For stricter enforcement, set the level to `"error"`. Also consider `eslint-plugin-sonarjs` which provides `cognitive-complexity` for a more nuanced measure.
- **Python projects**: Install `radon` (`pip install radon`) and add it to CI. Run `radon cc . -a -nc` to report functions with complexity above C grade. Alternatively, enable ruff's `C901` rule (McCabe complexity): add `"C901"` to the `select` list in `[tool.ruff.lint]` and set `max-complexity = 10` under `[tool.ruff.lint.mccabe]`.
- **Go projects**: Install `gocyclo` (`go install github.com/fzipp/gocyclo/cmd/gocyclo@latest`) and run `gocyclo -over 10 .` to find complex functions. Add to `.golangci.yml` under `linters.enable: [gocyclo]` with `linters-settings.gocyclo.min-complexity: 10`.
- **SonarQube alternative**: If the project uses SonarQube, verify the quality profile includes complexity rules and the quality gate has a complexity threshold. Check `sonar-project.properties` for project configuration.
- Add complexity checks to CI as a dedicated step. For Python: `radon cc . -a -nc --total-average -nb` (fail on average above B). For JS/TS: the ESLint complexity rule will fail the lint step automatically.
- To remediate high-complexity functions: extract helper functions, replace complex conditionals with early returns, use lookup tables instead of long switch/if-else chains, and apply the Strategy pattern for behavioral branching.

## Criterion-Specific Exploration Steps

- Check ESLint config for `complexity` rule or `sonarjs/cognitive-complexity` rule
- Check `pyproject.toml` for ruff `C901` rule or `[tool.ruff.lint.mccabe]` section
- Check for `radon` in dev dependencies (`requirements-dev.txt`, `pyproject.toml`)
- Look for `.golangci.yml` with `gocyclo` or `cyclop` linter enabled
- Check for `sonar-project.properties` indicating SonarQube integration
- Search CI workflows for complexity-related commands or tools

## Criterion-Specific Verification Steps

- **TypeScript/JavaScript**: Run `npx eslint . --rule '{"complexity": ["error", 10]}'` and confirm the rule is active
- **Python**: Run `radon cc . -a -s` and confirm it produces output, or run `ruff check . --select C901` and verify it evaluates complexity
- **Go**: Run `gocyclo -over 10 .` and confirm it executes
- Verify the complexity threshold is configured (not just that the tool is installed) by checking the specific config value
