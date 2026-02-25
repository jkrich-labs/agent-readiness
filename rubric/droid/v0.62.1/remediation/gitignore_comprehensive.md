---
signal_name: Comprehensive Gitignore
---

## Criterion-Specific Fix Guidance

- Create or update `.gitignore` at the repository root to exclude all common sensitive and generated files.
- **Essential exclusions** that must be present:
  - **Secrets**: `.env`, `.env.local`, `.env.*.local`, `*.pem`, `*.key`, `credentials.json`, `service-account.json`
  - **Node.js**: `node_modules/`, `.npm/`, `.yarn/cache/`
  - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `*.egg-info/`, `dist/`, `build/`, `.eggs/`
  - **Build artifacts**: `dist/`, `build/`, `out/`, `.next/`, `.nuxt/`, `target/` (Rust/Java)
  - **IDE configs**: `.idea/`, `.vscode/` (or selectively keep `.vscode/settings.json`), `*.swp`, `*.swo`, `*~`
  - **OS files**: `.DS_Store`, `Thumbs.db`, `Desktop.ini`
  - **Test/coverage**: `.coverage`, `htmlcov/`, `coverage/`, `.nyc_output/`, `*.lcov`
- **Use gitignore.io**: Generate a comprehensive starting point at https://www.toptal.com/developers/gitignore or use `npx gitignore <language>`.
- **Per-language additions**:
  - Go: `vendor/` (if not vendoring), binary output directories
  - Rust: `target/`, `Cargo.lock` (for libraries, keep for binaries)
  - Java: `*.class`, `*.jar`, `.gradle/`, `build/`
- If files that should be ignored are already tracked, remove them from tracking: `git rm --cached <file>` then commit.
- For monorepos, a single root `.gitignore` is usually sufficient, but app-specific `.gitignore` files can be added in subdirectories for overrides.

## Criterion-Specific Exploration Steps

- Check if `.gitignore` exists at the repository root
- Review its contents for missing categories: secrets, node_modules, build artifacts, IDE configs, OS files
- Check if any files that should be ignored are currently tracked: `git ls-files | grep -E '\.env$|node_modules|__pycache__|\.DS_Store'`
- Identify the project languages to determine which language-specific patterns are needed
- Check subdirectories for additional `.gitignore` files

## Criterion-Specific Verification Steps

- Confirm `.gitignore` exists and contains patterns for `.env`, `node_modules` (if JS/TS), build artifacts, IDE configs, and OS files
- Run `git status` and verify no files matching ignored patterns appear as untracked
- Verify that `.env` files with actual secrets are not tracked: `git ls-files | grep '\.env'` should return nothing (or only `.env.example`)
- Check that the gitignore is not overly broad (e.g., ignoring `*.json` would be too aggressive)
