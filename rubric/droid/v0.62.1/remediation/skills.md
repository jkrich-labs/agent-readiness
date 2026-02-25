---
signal_name: Skills
---

## Criterion-Specific Fix Guidance

- Create a `.claude/skills/` directory (for Claude Code) or `.factory/skills/` directory (for Factory/Droid) at the repository root.
- Each skill file must be named `SKILL.md` or follow the pattern `*.skill.md` and contain at minimum a `name` and `description` field.
- **Minimal SKILL.md structure**:
  ```
  # Skill Name
  Description of what this skill does and when to invoke it.

  ## Steps
  1. Concrete step the agent should take
  2. Another step with specific commands or file paths
  ```
- Write skills for common developer workflows: running tests, deploying, adding a new feature module, debugging CI failures, handling database migrations.
- Skills should reference actual file paths, commands, and patterns from the repo rather than generic instructions.
- Each skill should be focused on a single task — prefer many small skills over one large catch-all skill.
- If the repo already has a `CLAUDE.md` or `AGENTS.md`, extract reusable workflow guidance from those files into discrete skill files.

## Criterion-Specific Exploration Steps

- Check if `.claude/` or `.factory/` directories already exist
- Review `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` for workflow guidance that could become skills
- Identify the most common development tasks (test, lint, build, deploy) and which commands they use
- Check `Makefile`, `package.json` scripts, `pyproject.toml` scripts, or `Taskfile.yml` for defined workflows

## Criterion-Specific Verification Steps

- Confirm `.claude/skills/` or `.factory/skills/` directory exists and contains at least one `.md` file
- Verify each skill file has a name (heading) and a description (body text with actionable steps)
- Validate that referenced commands and file paths in the skills actually exist in the repo
