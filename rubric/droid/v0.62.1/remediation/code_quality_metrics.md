---
signal_name: Code Quality Metrics
---

## Criterion-Specific Fix Guidance

- **Codecov (coverage tracking)**: Sign up at codecov.io and add the repository. Add a CI step to upload coverage reports: `- uses: codecov/codecov-action@v4` (GitHub Actions). Generate coverage in your test step: `pytest --cov=src --cov-report=xml` (Python) or `jest --coverage` (TypeScript/JavaScript). Codecov will automatically comment on PRs with coverage diffs.
- **SonarQube / SonarCloud**: Create a `sonar-project.properties` file with `sonar.projectKey`, `sonar.organization`, and `sonar.sources`. Add a CI step: `sonar-scanner` or use the `sonarcloud-github-action`. SonarCloud tracks complexity, duplications, maintainability rating, and code smells over time.
- **Python coverage enforcement**: Add `pytest-cov` to dev dependencies. Configure minimum coverage in `pyproject.toml`: `[tool.coverage.report] fail_under = 80`. This fails the test step if coverage drops below the threshold.
- **TypeScript/JavaScript coverage enforcement**: In `jest.config.ts`, add `coverageThreshold: { global: { branches: 80, functions: 80, lines: 80, statements: 80 } }`. Jest will fail if thresholds are not met.
- **Complexity tracking**: Use `radon` for Python (`radon cc src/ -a -nc` to show average complexity), or `eslint-plugin-complexity` for TypeScript. Configure complexity thresholds: `max-complexity: ["warn", 10]` in ESLint.
- **Code scanning APIs**: Enable GitHub Code Scanning with CodeQL. Add `.github/workflows/codeql.yml` using the `github/codeql-action` actions. This tracks security and quality issues over time in the Security tab.
- **Badge and visibility**: Add coverage/quality badges to `README.md` so metrics are visible. Codecov and SonarCloud both provide embeddable badge URLs.
- **Trend monitoring**: Configure the tool to track metrics over time, not just point-in-time. Codecov and SonarCloud both provide historical graphs. Set up notifications for metric regressions.

## Criterion-Specific Exploration Steps

- Check for existing coverage configuration: `grep -E 'coverage|codecov|coveralls' pyproject.toml package.json .github/workflows/*.yml`
- Look for SonarQube/SonarCloud configuration: `sonar-project.properties`, `.sonarcloud.properties`
- Check for CodeQL workflow: `.github/workflows/codeql*.yml`
- Search for coverage thresholds: `grep -rn 'fail_under\|coverageThreshold\|coverage.report' pyproject.toml jest.config.*`
- Check CI workflows for coverage upload steps
- Look for complexity checking tools: `grep -E 'radon|complexity|eslint-plugin-complexity' pyproject.toml package.json`
- Check for quality badges in README.md: `grep -E 'codecov.io\|sonarcloud.io\|codeclimate' README.md`

## Criterion-Specific Verification Steps

- Confirm coverage reports are generated during test runs (check for `coverage.xml`, `lcov.info`, or `coverage/` directory after running tests)
- Verify CI uploads coverage to an external service (Codecov, SonarCloud, or Coveralls)
- Check the external service dashboard shows historical data, not just the latest run
- Confirm coverage thresholds are enforced (reduce a threshold temporarily and verify the build fails)
- For SonarQube, verify the quality gate is configured and includes complexity/maintainability rules
