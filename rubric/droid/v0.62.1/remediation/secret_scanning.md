---
signal_name: Secret Scanning
---

## Criterion-Specific Fix Guidance

- **GitHub native secret scanning** (easiest): Enable via Settings -> Code security and analysis -> Secret scanning. This is free for public repos and available with GitHub Advanced Security for private repos. No config files needed.
- **gitleaks** (pre-commit + CI): Install gitleaks and add both a pre-commit hook and a CI step:
  - Pre-commit (`.pre-commit-config.yaml`):
    ```yaml
    - repo: https://github.com/gitleaks/gitleaks
      rev: v8.18.0
      hooks:
        - id: gitleaks
    ```
  - CI (`.github/workflows/ci.yml`):
    ```yaml
    - name: Run gitleaks
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    ```
- **detect-secrets** (Yelp): Install `detect-secrets` and generate a baseline: `detect-secrets scan > .secrets.baseline`. Add a pre-commit hook and CI check that runs `detect-secrets audit .secrets.baseline`.
- **trufflehog**: Run `trufflehog git file://. --only-verified` in CI to scan the full git history for verified secrets.
- **SonarQube**: If SonarQube is already in use, enable the "Secrets" rule category in the quality profile.
- Whichever tool you choose, ensure it scans on every PR (not just the default branch) to prevent secrets from being merged.

## Criterion-Specific Exploration Steps

- Check if GitHub secret scanning is already enabled: `gh api repos/{owner}/{repo} --jq '.security_and_analysis.secret_scanning.status'`
- Look for `.gitleaks.toml` or `.gitleaksignore` configuration files
- Check for `.secrets.baseline` (detect-secrets) in the repo
- Search `.pre-commit-config.yaml` for gitleaks, detect-secrets, or trufflehog hooks
- Search CI workflows for secret scanning steps or actions
- Check `sonar-project.properties` for SonarQube configuration

## Criterion-Specific Verification Steps

- Confirm at least one secret scanning mechanism is active: GitHub native, gitleaks config/action, detect-secrets baseline, trufflehog action, or SonarQube secrets rules
- For gitleaks: run `gitleaks detect --source .` locally and confirm it executes without configuration errors
- For detect-secrets: run `detect-secrets scan` and confirm it produces output
- Verify the scanning tool runs in CI by checking workflow files for the relevant step
