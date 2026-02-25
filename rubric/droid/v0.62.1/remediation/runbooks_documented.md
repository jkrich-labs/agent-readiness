---
signal_name: Runbooks Documented
---

## Criterion-Specific Fix Guidance

- Create a `runbooks/` directory at the repo root, or document runbook links in `README.md` or `CONTRIBUTING.md`.
- **If using a `runbooks/` directory**, add Markdown files for common operational procedures:
  - `runbooks/incident-response.md` — steps to follow during an outage
  - `runbooks/deployment.md` — how to deploy to staging/production, rollback procedures
  - `runbooks/database-migrations.md` — how to run migrations, handle failures, rollback
  - `runbooks/scaling.md` — how to scale services up/down, autoscaling configuration
- **If runbooks live externally** (Notion, Confluence, internal wiki), add a `RUNBOOKS.md` or a section in `README.md` that links to them with descriptive titles:
  ```markdown
  ## Runbooks
  - [Incident Response](https://notion.so/team/incident-response)
  - [Deployment Guide](https://confluence.company.com/deploy-guide)
  - [Database Runbook](https://wiki.internal/db-runbook)
  ```
- Each runbook should include: when to use it, prerequisites, step-by-step instructions, rollback/recovery steps, and escalation contacts.
- For repos with CI/CD pipelines, document the deployment pipeline stages and how to manually trigger or retry them.
- Keep runbooks versioned with the code so they stay synchronized with the system they describe.

## Criterion-Specific Exploration Steps

- Check for a `runbooks/` or `docs/runbooks/` directory
- Search `README.md`, `CONTRIBUTING.md`, and `AGENTS.md` for links to Notion, Confluence, or internal wiki pages
- Look for deployment documentation in `docs/`, `.github/`, or `deploy/` directories
- Check for `PLAYBOOK.md`, `OPERATIONS.md`, or `ON-CALL.md` files
- Search for keywords: "runbook", "playbook", "incident", "on-call", "escalation"

## Criterion-Specific Verification Steps

- Confirm either a `runbooks/` directory with at least one `.md` file exists, or runbook links are present in `README.md`/`CONTRIBUTING.md`
- Verify runbook links are not broken (if external URLs, check they are reachable; if repo paths, check they exist)
- Confirm runbooks contain actionable steps, not just titles or placeholders
