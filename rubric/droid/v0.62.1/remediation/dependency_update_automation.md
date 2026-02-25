---
signal_name: Dependency Update Automation
---

## Criterion-Specific Fix Guidance

- Configure **Dependabot** or **Renovate** to automatically create PRs for dependency updates.
- **Dependabot** (GitHub native): Create `.github/dependabot.yml`:
  ```yaml
  version: 2
  updates:
    - package-ecosystem: "pip"  # or npm, gomod, cargo, docker, github-actions
      directory: "/"
      schedule:
        interval: "weekly"
      reviewers:
        - "org/team-name"
      labels:
        - "dependencies"
      open-pull-requests-limit: 10
  ```
  Add multiple entries for each package ecosystem in the repo (e.g., one for `pip`, one for `github-actions`, one for `docker`).
- **Renovate** (more configurable): Add `renovate.json` at the repo root:
  ```json
  {
    "$schema": "https://docs.renovatebot.com/renovate-schema.json",
    "extends": ["config:recommended"],
    "labels": ["dependencies"],
    "automerge": false
  }
  ```
  Install the Renovate GitHub App on the repository, or self-host via `renovate` CLI.
- **Key configuration choices**:
  - Set `schedule.interval` to `weekly` to avoid PR noise (daily can be overwhelming).
  - Group related updates (e.g., all `@types/*` packages, all linting tools) to reduce PR count.
  - Enable automerge for minor/patch updates of well-tested dependencies to reduce manual toil.
  - Set `open-pull-requests-limit` to prevent overwhelming the team.
- For monorepos, add a separate entry per directory that has its own lockfile.

## Criterion-Specific Exploration Steps

- Check if `.github/dependabot.yml` already exists
- Check if `renovate.json`, `renovate.json5`, or `.renovaterc` exists
- Identify all package ecosystems in the repo: `package.json` (npm), `pyproject.toml`/`requirements.txt` (pip), `go.mod` (gomod), `Cargo.toml` (cargo), `Dockerfile` (docker), `.github/workflows/` (github-actions)
- Check if the Renovate GitHub App is installed on the repository
- Look for recent dependency update PRs to see if automation is already active

## Criterion-Specific Verification Steps

- Confirm `.github/dependabot.yml` or `renovate.json` exists and is valid
- Verify all package ecosystems present in the repo are covered by the configuration
- Check that the configuration specifies a reasonable schedule and PR limits
- For Dependabot: check the Insights tab -> Dependency graph -> Dependabot to see if it is active
