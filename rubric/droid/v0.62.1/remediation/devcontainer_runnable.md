---
signal_name: Dev Container Runnable
---

## Criterion-Specific Fix Guidance

- Ensure the devcontainer defined in `.devcontainer/devcontainer.json` can actually be built and run successfully.
- **Fix common build failures**:
  - Pin base image tags to specific versions (e.g., `mcr.microsoft.com/devcontainers/python:1-3.12`) rather than `latest` to avoid breakage.
  - If using a custom `Dockerfile`, ensure all `COPY` and `ADD` paths are relative to the `.devcontainer/` directory or use the `context` field.
  - Ensure `postCreateCommand` does not assume interactive input — all commands must run non-interactively.
- **Validate `postCreateCommand`**: This is the most common failure point. Ensure the install command works: `pip install -e '.[dev]'`, `npm ci`, `yarn install --frozen-lockfile`, etc. Test it manually first.
- **Feature compatibility**: If using devcontainer features, ensure they are compatible with your base image. Some features require specific OS bases (Debian vs Alpine).
- **Docker Compose integration**: If using `dockerComposeFile`, ensure the referenced compose file exists and the `service` field matches a service name in that file.
- **Resource limits**: If the container needs significant resources (e.g., for building large projects), add `"runArgs": ["--memory=4g"]` or similar.
- Add a CI workflow that builds the devcontainer on PRs to catch regressions:
  ```yaml
  - uses: devcontainers/ci@v0.3
    with:
      runCmd: echo "Devcontainer builds successfully"
  ```

## Criterion-Specific Exploration Steps

- Check `.devcontainer/devcontainer.json` exists and is valid JSON
- Look at the `image` or `dockerFile` field to identify the base
- Review `postCreateCommand` and verify referenced scripts/commands exist
- If a custom `Dockerfile` is used, check it for syntax errors and missing files
- Check if `.devcontainer/` references a `docker-compose.yml` and verify that file exists
- Look for `devcontainers/ci` in `.github/workflows/` for existing CI validation

## Criterion-Specific Verification Steps

- Run `devcontainer build --workspace-folder .` from the repo root and confirm it completes without errors
- Run `devcontainer up --workspace-folder .` and confirm the container starts
- If `devcontainer` CLI is not available, run `docker build -f .devcontainer/Dockerfile .devcontainer/` as a basic smoke test
- Verify `postCreateCommand` succeeds by running it inside the container
