---
signal_name: Build Command Documentation
---

## Criterion-Specific Fix Guidance

- Add a clearly labeled section in `README.md` or `AGENTS.md` documenting the build commands for the project.
- **Python projects**: Document `pip install -e .`, `uv sync`, `poetry install`, or whichever package manager the project uses. Include the exact command to build/compile if applicable (e.g., `python -m build`, `uv build`).
- **Node.js/TypeScript projects**: Document `npm install && npm run build`, `yarn install && yarn build`, or `pnpm install && pnpm build`. If the project uses a bundler (webpack, vite, esbuild), mention how to invoke it.
- **Go projects**: Document `go build ./...` or the specific build target.
- **Rust projects**: Document `cargo build` or `cargo build --release`.
- Use a consistent format with code blocks, e.g., a "Build" or "Development" section with fenced shell commands.
- If the project has multiple apps or workspaces, document the build command for each.
- Prefer `AGENTS.md` if the project already has one, since it is specifically designed for AI agent consumption.

## Criterion-Specific Exploration Steps

- Read `README.md` and check for a "Build", "Development", "Getting Started", or "Installation" section
- Check for `AGENTS.md` or `CLAUDE.md` at the repo root
- Identify the build system: look for `package.json` (scripts.build), `pyproject.toml`, `Makefile`, `Cargo.toml`, `go.mod`
- Check `package.json` scripts section for `build`, `compile`, or `dev` entries
- Check `pyproject.toml` for `[build-system]` and `[project.scripts]`

## Criterion-Specific Verification Steps

- Confirm `README.md` or `AGENTS.md` contains at least one build command in a code block (e.g., `npm run build`, `pip install`, `go build`)
- Verify the documented command actually works by running it in a clean checkout
- Grep for build-related keywords: `grep -i 'build\|install\|compile' README.md AGENTS.md`
