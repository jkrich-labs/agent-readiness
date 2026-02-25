---
signal_name: README
---

## Criterion-Specific Fix Guidance

- Create or enhance `README.md` at the repository root.
- Must include: project name, one-paragraph description of what the project does, setup/installation instructions, and basic usage examples.
- If the repo has multiple apps (monorepo), the root README should explain the repo structure and link to app-specific READMEs.
- Include build and test commands so developers (human or AI) can get started quickly.
- Keep it concise — a good README is 50-200 lines, not a novel.

## Criterion-Specific Exploration Steps

- Check if `README.md` exists at the repository root
- If it exists, check whether it contains setup instructions and usage information
- Check for app-level READMEs in subdirectories

## Criterion-Specific Verification Steps

- Confirm `README.md` exists and has substantive content (>100 characters, not just a title)
- Verify it mentions at least one build or test command
