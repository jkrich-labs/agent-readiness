---
signal_name: Dev Container
---

## Criterion-Specific Fix Guidance

- Create `.devcontainer/devcontainer.json` at the repository root.
- **Minimal devcontainer.json**:
  ```json
  {
    "name": "Project Dev Environment",
    "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
    "features": {},
    "postCreateCommand": "echo 'Setup complete'",
    "customizations": {
      "vscode": {
        "extensions": []
      }
    }
  }
  ```
- **Python projects**: Use `mcr.microsoft.com/devcontainers/python:3.12` as the base image. Add a `postCreateCommand` that runs `pip install -e '.[dev]'` or `uv sync --extra dev`. Add extensions like `ms-python.python`, `charliermarsh.ruff`.
- **TypeScript/JavaScript projects**: Use `mcr.microsoft.com/devcontainers/typescript-node:20` as the base image. Set `postCreateCommand` to `npm install` or `yarn install`. Add extensions like `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`.
- **Multi-language repos**: Use the base Ubuntu image and add language features via the `features` field (e.g., `"ghcr.io/devcontainers/features/python:1": {}`, `"ghcr.io/devcontainers/features/node:1": {}`).
- If the project uses Docker Compose for local services, reference it via `"dockerComposeFile"` and `"service"` fields instead of a standalone image.
- Add `forwardPorts` for any services the developer needs to access (e.g., `[3000, 8000, 5432]`).
- Set `"remoteUser": "vscode"` to avoid running as root.

## Criterion-Specific Exploration Steps

- Check if `.devcontainer/` directory already exists
- Identify the project languages and runtimes from `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`
- Check for `docker-compose.yml` to understand local service dependencies
- Review `Dockerfile` if one exists — it may be a good base for the devcontainer
- Check what VS Code extensions are recommended in `.vscode/extensions.json`

## Criterion-Specific Verification Steps

- Confirm `.devcontainer/devcontainer.json` exists and is valid JSON
- If `devcontainer` CLI is installed, run `devcontainer build --workspace-folder .` to verify it builds
- Verify the `postCreateCommand` references valid install commands for the project
