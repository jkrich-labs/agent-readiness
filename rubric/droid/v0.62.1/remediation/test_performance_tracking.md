---
signal_name: Test Performance Tracking
---

## Criterion-Specific Fix Guidance

- **Python projects**: Add `--durations=10` to pytest invocation to report the 10 slowest tests. Configure in `pyproject.toml`: `[tool.pytest.ini_options]` with `addopts = "--durations=10 -v"`. For full timing data, use `pytest --junit-xml=report.xml` which includes per-test durations in JUnit format.
- **TypeScript/JavaScript (Jest) projects**: Use `--verbose` flag to show per-test timing. Add `"test:ci": "jest --verbose --ci --reporters=default --reporters=jest-junit"` to `package.json`. Install `jest-junit` (`npm install -D jest-junit`) for JUnit XML reports with timing data.
- **TypeScript/JavaScript (Vitest) projects**: Use `vitest run --reporter=verbose --reporter=junit --outputFile=report.xml` to produce timing reports.
- **Upload test reports as CI artifacts**: In GitHub Actions, add a step after tests:
  ```yaml
  - uses: actions/upload-artifact@v4
    if: always()
    with:
      name: test-results
      path: report.xml
  ```
- **Track trends over time**: Use tools like `test-results-reporter` GitHub Action or BuildPulse to visualize test duration trends and catch performance regressions.
- Configure CI to produce JUnit XML reports and upload them as artifacts. This enables historical tracking and identification of tests that are getting slower.
- Mark slow tests with `@pytest.mark.slow` or Jest `--detectOpenHandles` to identify tests that hang or take unexpectedly long.

## Criterion-Specific Exploration Steps

- Check `pyproject.toml` for `--durations` in pytest `addopts`
- Check `package.json` for `--verbose` or `--ci` flags in test scripts
- Check for `jest-junit`, `vitest` reporter configuration, or `mocha-junit-reporter` in `devDependencies`
- Look at CI workflows for `upload-artifact` steps that save test reports
- Check for JUnit XML output configuration (`--junit-xml`, `--reporters=jest-junit`)
- Look for test report visualization tools (Allure, ReportPortal, BuildPulse) in CI config

## Criterion-Specific Verification Steps

- Run tests and confirm timing information is printed in the output (e.g., `--durations` output for pytest, per-test times for Jest verbose)
- Verify JUnit XML report is generated and contains `time` attributes on test cases
- Check that CI workflow uploads test report artifacts after the test step
- Confirm the `if: always()` condition is set on the upload step so reports are saved even on test failure
