---
signal_name: Error to Insight Pipeline
---

## Criterion-Specific Fix Guidance

- **Sentry-GitHub integration**: In Sentry project settings, navigate to Integrations and connect GitHub. This enables: (1) automatic issue creation in GitHub from Sentry errors, (2) suspect commit detection linking errors to the commit that introduced them, (3) stack trace linking to source code in GitHub. Configure by mapping Sentry projects to GitHub repositories.
- **Sentry auto-assignment**: Configure Sentry's issue ownership rules to automatically assign errors to the developer who last modified the relevant code. In Sentry project settings under Ownership Rules, add patterns like `path:src/auth/* #team-auth` or `url:*/api/payments/* #team-payments`. This closes the loop from error to responsible engineer.
- **Sentry Alerts to GitHub Issues**: Create a Sentry alert rule that automatically creates a GitHub issue when a new error occurs or an error regresses. In Sentry: Alerts > Create Alert Rule > Action: Create a GitHub Issue. Configure the target repository and assign to a team or individual.
- **Error-to-issue automation (custom)**: If not using Sentry, build a custom integration using webhooks. Configure your error tracking tool to send webhooks to a serverless function (Lambda, Cloud Function) that creates GitHub issues via the GitHub API. Include: error title, stack trace, frequency, affected users, and a link back to the error tracking dashboard.
- **Linear/Jira integration**: Sentry also integrates with Linear and Jira. For Linear: connect via Sentry Integrations > Linear. For Jira: use the Sentry Jira plugin. Errors can auto-create tickets with appropriate priority based on error frequency and user impact.
- **GitHub Actions error workflow**: Create a GitHub Action that monitors error tracking APIs and creates issues for new errors: use a scheduled workflow (`cron: '0 */6 * * *'`) that calls the Sentry API (`GET /api/0/projects/{org}/{project}/issues/?query=is:unresolved firstSeen:>24h`), filters for high-priority errors, and creates GitHub issues for any that do not already have one.
- **Release correlation**: Ensure Sentry releases are tagged with the git SHA and environment. This enables "introduced in release" and "resolved in release" tracking. Add `sentry-cli releases set-commits VERSION --auto` to the deploy pipeline.
- **Feedback loop metrics**: Track the time from error occurrence to issue creation and from issue creation to resolution. This measures the effectiveness of the pipeline. Use Sentry's issue resolution data or GitHub issue metrics.

## Criterion-Specific Exploration Steps

- Check Sentry configuration for GitHub integration: look for `SENTRY_ORG`, `SENTRY_PROJECT`, `SENTRY_AUTH_TOKEN` in environment variables or CI configs
- Search for Sentry release tracking: `grep -rn 'sentry-cli\|SENTRY_RELEASE\|sentry.*release' .github/workflows/ Makefile`
- Check for webhook integrations: `grep -rn 'webhook\|sentry.*github\|error.*issue\|error.*ticket' .github/workflows/ src/`
- Look for Sentry alert rule configuration in IaC: `grep -rn 'sentry_rule\|sentry_project_rule' terraform/`
- Check for existing error-to-issue automation: `grep -rn 'create.*issue\|gh issue create\|linear.*create' .github/workflows/ scripts/`
- Verify Sentry SDK has release tracking configured: `grep -rn 'release.*=\|SENTRY_RELEASE' src/ .env*`
- Check the Sentry project dashboard (if accessible) for existing GitHub integration status

## Criterion-Specific Verification Steps

- Confirm a Sentry-GitHub (or equivalent) integration is active by checking Sentry project settings or the configured webhook
- Trigger a test error in a staging environment and verify it appears in Sentry with the correct release tag and linked to the source commit
- Verify that a new, high-frequency error results in an automatically created GitHub issue (or equivalent in Linear/Jira)
- Check that auto-created issues contain useful context: error message, stack trace or link, frequency, and affected user count
- Verify suspect commits are detected: introduce an error intentionally and confirm Sentry identifies the commit
- Confirm the error tracking tool can mark issues as resolved when a fix is deployed (release-based resolution)
- Check that ownership rules are configured so errors are assigned to the appropriate team
