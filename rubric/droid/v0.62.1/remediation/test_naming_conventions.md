---
signal_name: Test Naming Conventions
---

## Criterion-Specific Fix Guidance

- **Python projects**: Enforce `test_*.py` file naming and `test_*` function naming by configuring pytest discovery in `pyproject.toml`: `[tool.pytest.ini_options]` with `python_files = ["test_*.py"]`, `python_classes = ["Test*"]`, `python_functions = ["test_*"]`. This ensures pytest only discovers consistently named tests.
- **TypeScript/JavaScript projects**: Enforce `*.test.ts` or `*.spec.ts` naming by configuring the test framework. For Jest: set `testMatch` in `jest.config.ts`: `testMatch: ["**/*.test.ts", "**/*.test.tsx"]`. For Vitest: set `include` in `vitest.config.ts`: `test: { include: ["**/*.test.ts"] }`.
- **Go projects**: Go enforces `*_test.go` naming by convention (the `go test` tool only discovers files matching this pattern). No additional configuration needed, but document the convention in `CONTRIBUTING.md`.
- **Document conventions**: Add a testing section to `CONTRIBUTING.md` or a `TESTING.md` file that specifies:
  - File naming pattern (e.g., `test_*.py`, `*.test.ts`, `*_test.go`)
  - Test function naming pattern (e.g., `test_should_do_something`, `it('should do something')`)
  - Test file location (co-located with source or in `tests/` directory)
- Use ESLint rules to enforce test naming in JavaScript/TypeScript: `eslint-plugin-jest` provides `jest/valid-title` and `jest/consistent-test-it` rules.
- Configure CI to validate test naming by running discovery and checking that all test files match the expected pattern.

## Criterion-Specific Exploration Steps

- Check `pyproject.toml` for `[tool.pytest.ini_options]` with `python_files`, `python_classes`, `python_functions` settings
- Check `jest.config.*` for `testMatch` or `testRegex` settings
- Check `vitest.config.*` for `include` or `exclude` patterns in test options
- Look for `CONTRIBUTING.md`, `TESTING.md`, or `CONVENTIONS.md` that documents test naming rules
- Check ESLint config for `jest/valid-title` or `jest/consistent-test-it` rules
- Scan actual test files to see if naming is already consistent (all `test_*.py` or all `*.test.ts`)
- Check for test files that violate the expected naming convention

## Criterion-Specific Verification Steps

- **Python**: Run `pytest --collect-only` and confirm all discovered tests follow the `test_*` naming convention
- **TypeScript/JavaScript**: Verify `jest.config.*` has `testMatch` configured, and run `npx jest --listTests` to confirm only matching files are discovered
- **Go**: Verify all test files end in `_test.go` (this is enforced by the Go toolchain)
- Check that naming conventions are either enforced via tool configuration or documented in a contributing guide
- Verify there are no test files with non-standard names that are silently ignored by the test framework
