---
signal_name: VCS CLI Tools
---

## Criterion-Specific Fix Guidance

- **Install GitHub CLI (`gh`)**: Follow instructions at https://cli.github.com/. On macOS: `brew install gh`. On Ubuntu/Debian: `sudo apt install gh` or via the official APT repository. On Fedora: `sudo dnf install gh`.
- **Authenticate**: Run `gh auth login` and follow the interactive prompts. Choose HTTPS protocol and authenticate via browser or token. For CI, set `GH_TOKEN` environment variable with a Personal Access Token (PAT) or use `GITHUB_TOKEN` provided by GitHub Actions.
- **GitLab CLI (`glab`)**: If the repo is hosted on GitLab, install `glab` (`brew install glab` on macOS, or from https://gitlab.com/gitlab-org/cli). Authenticate with `glab auth login`.
- **Verify authentication**: Run `gh auth status` to confirm the CLI is authenticated and has the required scopes. Minimum scopes needed: `repo`, `read:org`.
- **CI integration**: GitHub Actions automatically provides `GITHUB_TOKEN`. For other CI systems, create a PAT with `repo` scope and set it as `GH_TOKEN` secret.
- **Dev container / Codespace**: If using devcontainers, add `"ghcr.io/devcontainers/features/github-cli:1": {}` to `.devcontainer/devcontainer.json` features to ensure `gh` is available.

## Criterion-Specific Exploration Steps

- Check if `gh` is installed: `which gh` or `gh --version`
- Check authentication status: `gh auth status`
- Determine the VCS host (GitHub vs GitLab) by inspecting `git remote -v`
- Check if `glab` is installed for GitLab repos: `which glab`
- Check CI environment for token availability: look for `GH_TOKEN` or `GITHUB_TOKEN` in workflow files

## Criterion-Specific Verification Steps

- Run `gh auth status` and confirm it reports a valid authentication with appropriate scopes
- Run a simple API call to verify access: `gh api repos/{owner}/{repo}` should return repo metadata
- For GitLab: `glab auth status` should report successful authentication
