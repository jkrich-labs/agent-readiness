---
signal_name: AGENTS.md
---

## Criterion-Specific Fix Guidance

- Create an `AGENTS.md` file at the repository root with at least 100 characters of substantive content.
- **Required sections**: At minimum include: (1) what the project does (1-2 sentences), (2) how to build it, and (3) how to run tests.
- **Build commands**: List the exact commands to install dependencies and build the project. Example: `npm install && npm run build` or `uv sync && uv run python -m build`.
- **Test commands**: List the exact commands to run the test suite. Example: `npm test`, `uv run pytest`, `go test ./...`. Include how to run a single test file or test case.
- **Architecture overview**: Briefly describe the project structure, key directories, and the main entry points. This helps AI agents navigate the codebase efficiently.
- **Coding conventions**: Document any non-obvious conventions: naming patterns, import ordering, preferred libraries, error handling patterns. This prevents AI agents from introducing inconsistent code.
- **Environment setup**: Document required environment variables (reference `.env.example`), system dependencies, and any one-time setup steps.
- **Do not duplicate README**: `AGENTS.md` is optimized for AI agent consumption. It should be dense, command-focused, and skip marketing/badges/screenshots that are useful for humans but noise for agents.

## Criterion-Specific Exploration Steps

- Check if `AGENTS.md` already exists at the repo root: `ls -la AGENTS.md`
- If it exists, check its length: `wc -c AGENTS.md` (must be >100 characters)
- Check for alternative agent config files that could be referenced: `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`
- Read `README.md` to understand what build/test commands should be documented in `AGENTS.md`
- Check `package.json` scripts, `Makefile`, or `pyproject.toml` for the canonical build and test commands

## Criterion-Specific Verification Steps

- Confirm `AGENTS.md` exists at the repository root
- Verify it has more than 100 characters of content: `wc -c AGENTS.md`
- Verify it contains at least one build command and one test command
- Ensure the documented commands actually work when executed
