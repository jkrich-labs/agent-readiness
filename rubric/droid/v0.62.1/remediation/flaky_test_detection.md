---
signal_name: Flaky Test Detection
---

## Criterion-Specific Fix Guidance

- **Jest projects**: Install `jest-circus` (default in Jest 27+) and configure retries: `jest.retryTimes(2)` in test setup or `--retries=2` CLI flag. Track which tests needed retries to identify flaky tests. Use `jest-flaky-test-reporter` for automated reporting.
- **Vitest projects**: Configure retries in `vitest.config.ts`: `test: { retry: 2 }`. Tests that pass on retry are flagged as flaky in the output.
- **Python (pytest) projects**: Install `pytest-rerunfailures` (`pip install pytest-rerunfailures`) and add `--reruns 2 --reruns-delay 1` to pytest invocation. This reruns failed tests and marks them as flaky if they pass on retry. Configure in `pyproject.toml`: `addopts = "--reruns 2"`.
- **BuildPulse integration**: Sign up for BuildPulse (buildpulse.io) and add their GitHub Action to CI. It analyzes JUnit XML reports across builds to automatically detect and track flaky tests. Add after test step:
  ```yaml
  - uses: Workshop64/buildpulse-action@main
    with:
      account-id: $ACCOUNT_ID
      repository-id: $REPO_ID
      path: report.xml
  ```
- **Quarantine mechanism**: Create a quarantine list of known flaky tests. In pytest: use a custom marker `@pytest.mark.flaky` and configure CI to run quarantined tests separately with `--allow-flaky`. In Jest: use `test.skip` or a custom `quarantine.json` list.
- This criterion is skippable: if the test suite is small or has no history of flaky tests, it may not be applicable.
- The key goal is proactive management: detecting flaky tests before they erode developer trust in CI.

## Criterion-Specific Exploration Steps

- Check `package.json` for `jest-circus`, retry configuration, or flaky test plugins
- Check `vitest.config.*` for `retry` setting in test options
- Check Python dev dependencies for `pytest-rerunfailures` or `flaky`
- Check `pyproject.toml` for `--reruns` in pytest `addopts`
- Look for BuildPulse, Launchable, or similar flaky test tracking tools in CI workflows
- Search for `retryTimes`, `retry`, `rerun`, or `flaky` in test config files
- Look for quarantine lists or skip annotations that indicate known flaky tests

## Criterion-Specific Verification Steps

- **Jest**: Verify `jest.retryTimes` is configured in test setup or global config
- **pytest**: Run `pytest --reruns 0 --co` and confirm the `pytest-rerunfailures` plugin is loaded (appears in header)
- **Vitest**: Verify `retry` is set in `vitest.config.ts`
- Check CI logs for retry output indicating the mechanism is active
- Verify flaky test detection is configured to report (not just silently retry)
