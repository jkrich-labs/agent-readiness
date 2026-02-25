---
signal_name: Environment Template
---

## Criterion-Specific Fix Guidance

- Create a `.env.example` file at the repository root listing every environment variable the project needs, with placeholder or default values.
- **Format each line** as `VARIABLE_NAME=placeholder_value` with a comment above or inline explaining the variable's purpose:
  ```
  # Database connection string
  DATABASE_URL=postgresql://user:password@localhost:5432/mydb
  # API key for external service (get from team vault)
  API_KEY=your-api-key-here
  # Set to "true" to enable debug mode
  DEBUG=false
  ```
- Never include real secrets in `.env.example` — use clearly fake placeholders like `your-api-key-here`, `changeme`, or `xxx`.
- **Alternative**: If the project does not use `.env` files, document all required environment variables in `README.md` or `AGENTS.md` under a dedicated "Environment Variables" section with a table of variable names, descriptions, and example values.
- For monorepos, consider per-app `.env.example` files (e.g., `backend/.env.example`, `frontend/.env.example`) in addition to a root-level one.
- Ensure `.env` (the real file) is in `.gitignore` so actual secrets are never committed.
- If using Docker Compose, reference the `.env.example` in `env_file` with a comment pointing developers to copy it.

## Criterion-Specific Exploration Steps

- Check if `.env.example`, `.env.sample`, or `.env.template` already exists
- Search for `os.environ`, `process.env`, `os.Getenv`, or `env::var` in source code to find all referenced environment variables
- Check `docker-compose.yml` for `environment:` or `env_file:` sections
- Look at `README.md` or `AGENTS.md` for any existing env var documentation
- Verify `.env` is listed in `.gitignore`

## Criterion-Specific Verification Steps

- Confirm `.env.example` exists at the repo root (or env vars are documented in README/AGENTS.md)
- Verify every environment variable used in the codebase is represented in `.env.example`
- Confirm `.env.example` does not contain real secrets (no actual API keys, passwords, or tokens)
- Confirm `.env` is gitignored
