---
signal_name: Single Command Setup
---

## Criterion-Specific Fix Guidance

- **Document a single setup command** in `README.md` or `AGENTS.md` that takes a developer from `git clone` to a running dev server in one step.
- **Makefile approach**: Create a `Makefile` with a `setup` or `dev` target that installs dependencies, runs migrations, seeds data, and starts the dev server. Document: `make dev` in the README.
- **Script approach**: Create a `scripts/setup.sh` (or `bin/setup`) that performs all setup steps. Make it idempotent so running it twice is safe. Document: `./scripts/setup.sh` in the README.
- **Python projects**: Aim for `uv sync && uv run <entrypoint>` or `pip install -e . && python -m <module>`. If the project needs environment variables, include a `.env.example` and document `cp .env.example .env` as a prerequisite.
- **Node.js projects**: Aim for `npm install && npm run dev` or ideally `npm start`. If additional setup is needed (database, env vars), wrap everything in a single script.
- **Docker Compose**: If the project uses Docker, `docker compose up` can serve as the single command. Document it clearly.
- **Dev containers**: A `.devcontainer/devcontainer.json` with `postCreateCommand` that runs setup automatically satisfies this criterion.
- **Key principle**: A new developer (or AI agent) should not need to read multiple docs or run more than 2-3 commands to get a working development environment.

## Criterion-Specific Exploration Steps

- Read `README.md` and `AGENTS.md` for setup instructions; check if they describe a single command workflow
- Check for `Makefile`, `scripts/setup.sh`, `bin/setup`, or `docker-compose.yml`
- Check for `.devcontainer/devcontainer.json` with `postCreateCommand`
- Identify all prerequisites: databases, environment variables, system dependencies
- Try the documented setup steps and note any gaps or manual steps required

## Criterion-Specific Verification Steps

- Confirm that `README.md` or `AGENTS.md` documents a clone-to-running flow in 1-3 commands
- Verify the documented command(s) actually work in a clean environment (fresh clone, no prior state)
- The setup command should complete without interactive prompts or manual intervention
