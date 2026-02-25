---
signal_name: Unit Tests Exist
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Create test files following the `*.test.ts` or `*.spec.ts` naming convention alongside source files, or in a `__tests__/` directory. Install a test framework: Jest (`npm install -D jest @types/jest ts-jest`) or Vitest (`npm install -D vitest`). Create at least one test file that imports and tests a module.
- **Python projects**: Create test files following the `test_*.py` naming convention in a `tests/` directory at the app or repo root. Install pytest (`pip install pytest`) and add it to dev dependencies. Create at least one test file with a function named `test_*` that asserts expected behavior.
- **Jest setup for TypeScript**: Create `jest.config.ts` with `preset: 'ts-jest'` and `testEnvironment: 'node'`. Add a `test` script to `package.json`: `"test": "jest"`.
- **Vitest setup**: Create `vitest.config.ts` and add `"test": "vitest run"` to `package.json` scripts. Vitest works out of the box with Vite projects and supports TypeScript natively.
- **pytest setup**: Ensure `pyproject.toml` has `[tool.pytest.ini_options]` with `testpaths = ["tests"]`. Run `pytest` to verify discovery.
- Place tests close to the code they test: `src/utils/helper.ts` should have `src/utils/helper.test.ts` or `tests/utils/test_helper.py`.
- A minimal starting point: write one test per module that verifies the primary exported function or class behaves correctly for a basic input.

## Criterion-Specific Exploration Steps

- Search for `*.test.ts`, `*.test.js`, `*.spec.ts`, `*.spec.js` files anywhere in the project
- Search for `test_*.py` or `*_test.py` files in `tests/` or alongside source files
- Check for a `__tests__/` directory
- Check `package.json` for `jest`, `vitest`, `mocha`, or `ava` in `devDependencies`
- Check Python dependencies for `pytest`, `unittest`, or `nose`
- Check for test configuration: `jest.config.*`, `vitest.config.*`, `pytest.ini`, `pyproject.toml` `[tool.pytest]`

## Criterion-Specific Verification Steps

- Confirm at least one test file exists matching the expected naming pattern (`*.test.ts` or `test_*.py`)
- Verify the test file contains actual test cases (not empty files or only imports)
- Run `npx jest --listTests` or `pytest --collect-only` to confirm the test framework discovers the tests
- Check that tests are not all skipped or marked as `TODO`
