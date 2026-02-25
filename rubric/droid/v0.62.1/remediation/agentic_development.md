---
signal_name: Agentic Development
---

## Criterion-Specific Fix Guidance

- **Git co-authorship**: When AI agents contribute code, include `Co-Authored-By` trailers in commit messages (e.g., `Co-Authored-By: Claude <noreply@anthropic.com>`). This is standard Git convention and shows up in GitHub's contributor graph.
- **Agent config directories**: Create configuration files for AI coding agents at the repo root: `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, or `.aider.conf.yml`. These files provide context to agents working on the codebase.
- **CI-invoked agents**: Configure workflows where AI agents are triggered by CI events. Examples: Droid running on PRs, Copilot Workspace triggered by issues, or custom actions that invoke Claude or GPT APIs for code review or generation.
- **Agent-friendly documentation**: Ensure `AGENTS.md` or `CLAUDE.md` documents build commands, test commands, architecture decisions, and coding conventions so agents can operate autonomously.
- **PR authorship signals**: Agent-authored PRs typically have bot labels, specific author names (e.g., `dependabot`, `droid`), or explicit mentions in PR descriptions. Configure your workflow to label agent-created PRs.
- **Aider / Claude Code / Cursor**: If developers use these tools, their commit messages typically contain co-authorship markers. Encourage consistent usage of `--co-author` flags or similar settings.

## Criterion-Specific Exploration Steps

- Search git history for co-authorship markers: `git log --all --grep='Co-Authored-By' --oneline | head -20`
- Check for agent config files: `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`, `.aider.conf.yml`, `.continue/config.json`
- Look at CI workflows for agent invocation (actions that call AI APIs or run agent tools)
- Check for `.droid/` directory or droid configuration
- Look at recent PRs for bot authors or agent-related labels

## Criterion-Specific Verification Steps

- Confirm at least one of: (a) co-authorship trailers exist in recent commit history, (b) an agent config file exists at the repo root, or (c) CI workflows invoke AI agents
- Run `git log --oneline -50 | grep -i 'co-authored\|copilot\|claude\|aider\|droid'` to check for agent traces
- Verify agent config files contain substantive content (not just a placeholder)
