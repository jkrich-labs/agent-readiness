---
signal_name: Test Coverage Thresholds
---

## Criterion-Specific Fix Guidance

- **Jest projects**: Add `coverageThreshold` to `jest.config.ts` or `jest.config.js`:
  ```json
  "coverageThreshold": {
    "global": {
      "branches": 70,
      "functions": 70,
      "lines": 80,
      "statements": 80
    }
  }
  ```
  Add `--coverage` to the test script: `"test:ci": "jest --coverage"`. This fails the test run if coverage drops below thresholds.
- **Vitest projects**: Add coverage configuration in `vitest.config.ts`: `test: { coverage: { provider: 'v8', thresholds: { lines: 80, branches: 70, functions: 70 } } }`. Install the provider: `npm install -D @vitest/coverage-v8`.
- **Python (pytest) projects**: Install `pytest-cov` (`pip install pytest-cov`) and add `--cov=src --cov-fail-under=80` to pytest invocation. Configure in `pyproject.toml`: `[tool.pytest.ini_options]` with `addopts = "--cov=src --cov-fail-under=80 --cov-report=term-missing"`. The `--cov-fail-under` flag fails the test run if overall coverage is below the threshold.
- **Codecov / Coveralls integration**: Add a coverage upload step to CI and configure coverage gates. For Codecov, create a `codecov.yml` with `coverage: status: project: default: target: 80%` to require a minimum coverage percentage on PRs.
- Start with achievable thresholds based on current coverage (run coverage once to see the baseline), then ratchet up over time.
- Use `--cov-report=html` (Python) or `--coverage --coverageReporters=html` (Jest) to generate visual reports for identifying untested code.

## Criterion-Specific Exploration Steps

- Check `jest.config.*` for `coverageThreshold` setting
- Check `vitest.config.*` for `coverage.thresholds` setting
- Check `pyproject.toml` for `--cov-fail-under` in pytest `addopts` or `[tool.coverage.report]` `fail_under`
- Check for `.coveragerc` or `setup.cfg` `[coverage:report]` section with `fail_under`
- Check for `codecov.yml`, `.coveralls.yml`, or coverage service configuration
- Check `package.json` for `nyc` (Istanbul) configuration with `check-coverage` and thresholds
- Look at CI workflows for coverage upload steps (Codecov action, coveralls action)

## Criterion-Specific Verification Steps

- **Jest**: Run `npx jest --coverage` and confirm the coverage summary includes threshold checking (shows PASS/FAIL against thresholds)
- **Python**: Run `pytest --cov=src --cov-fail-under=80` and confirm it enforces the threshold (exits non-zero if below)
- Verify the threshold is set to a meaningful value (not 0% or unrealistically low)
- Check that CI runs tests with coverage enabled and the threshold flag is active
- If using Codecov/Coveralls: verify the configuration file has a `target` or `threshold` set
