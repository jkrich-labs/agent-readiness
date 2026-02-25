---
signal_name: Automated Security Review
---

## Criterion-Specific Fix Guidance

- Add at least one automated SAST (Static Application Security Testing) tool to the CI pipeline.
- **GitHub native**: Enable Dependabot security alerts and CodeQL analysis. Add `.github/workflows/codeql.yml`:
  ```yaml
  name: CodeQL
  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]
  jobs:
    analyze:
      runs-on: ubuntu-latest
      permissions:
        security-events: write
      steps:
        - uses: actions/checkout@v4
        - uses: github/codeql-action/init@v3
          with:
            languages: python  # or javascript, typescript, go, etc.
        - uses: github/codeql-action/analyze@v3
  ```
- **Snyk**: Add Snyk to CI with `snyk test` (dependency vulnerabilities) and `snyk code test` (SAST). Configure via `.snyk` policy file if needed.
- **Python projects**: Add `bandit` for security linting (`bandit -r src/`) and `safety` or `pip-audit` for dependency scanning. Integrate into CI or pre-commit.
- **TypeScript/JavaScript projects**: Add `npm audit` or `yarn audit` to CI. Consider `eslint-plugin-security` for static analysis.
- **SonarQube**: If SonarQube is configured, ensure the quality profile includes security rules (OWASP Top 10, CWE categories) and that the quality gate fails on new security hotspots.
- **Dependabot audit reports**: Enable Dependabot alerts and configure `.github/dependabot.yml` to also run `audit` checks.
- Ensure security scan results are visible in PRs (as comments, check annotations, or status checks) so issues are caught before merge.

## Criterion-Specific Exploration Steps

- Check `.github/workflows/` for CodeQL, Snyk, or other security scanning actions
- Look for `.snyk` policy file, `bandit.yml`, `.semgrep.yml`, or `sonar-project.properties`
- Check if Dependabot alerts are enabled: `gh api repos/{owner}/{repo}/vulnerability-alerts` (returns 204 if enabled)
- Search CI workflows for `npm audit`, `pip-audit`, `safety check`, `bandit`, `semgrep`
- Check for SARIF file uploads in CI (used by GitHub code scanning)

## Criterion-Specific Verification Steps

- Confirm at least one security scanning tool is configured in CI and runs on PRs
- Run the security scanner locally to verify it executes without configuration errors
- Check GitHub Security tab for any existing alerts or code scanning results
- Verify the scanner is configured to fail the build (or at minimum report) on high-severity findings
