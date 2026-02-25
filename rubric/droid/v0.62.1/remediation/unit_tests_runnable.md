---
signal_name: Unit Tests Runnable
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Ensure `package.json` has a `"test"` script that runs the test suite. Common configurations: `"test": "jest"`, `"test": "vitest run"`, `"test": "mocha"`. Run `npm test` or `yarn test` to verify it exits without errors. If using Jest with TypeScript, ensure `ts-jest` or `@swc/jest` is configured as the transform.
- **Python projects**: Ensure `pytest` can discover and run tests. Verify by running `pytest --collect-only` to list discovered tests, then `pytest` to execute them. If tests fail to collect, check that `pyproject.toml` has `[tool.pytest.ini_options]` with correct `testpaths` and that test files follow `test_*.py` naming.
- Fix common issues that prevent tests from running:
  - **Missing dependencies**: Run `npm install` or `pip install -e ".[dev]"` to install dev dependencies
  - **Config errors**: Verify `jest.config.*` or `vitest.config.*` exists and has valid syntax
  - **Import errors**: Ensure `tsconfig.json` paths and module resolution are correct; for Python, ensure the package is installed in editable mode
  - **Environment variables**: Check if tests require `.env` files or specific environment setup
- Add `"test"` script to `package.json` if it is missing. For Python, document the test command in `pyproject.toml` scripts or in the README.
- Verify tests can run in CI by checking the workflow file for a test step and confirming it uses the same command.

## Criterion-Specific Exploration Steps

- Check `package.json` for a `"test"` script and what command it runs
- Check `pyproject.toml` for `[tool.pytest.ini_options]` configuration
- Look for test config files: `jest.config.*`, `vitest.config.*`, `pytest.ini`, `setup.cfg` `[tool:pytest]`
- Check if `node_modules/` or virtual environment exists (dependencies installed)
- Look for `.env.test` or `.env.example` files that may be needed for test execution
- Check CI workflows for the test command to see what is expected to work

## Criterion-Specific Verification Steps

- **TypeScript/JavaScript**: Run `npm test -- --listTests` (Jest) or `npx vitest run --reporter=verbose` and confirm tests are discovered and at least one passes
- **Python**: Run `pytest --collect-only` and confirm it discovers tests without errors, then run `pytest` and confirm at least one test passes
- Verify the test command exits with code 0 (no test failures or configuration errors)
- Check that the test framework produces output (not silently skipping everything)
