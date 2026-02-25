---
signal_name: Rollback Automation
---

## Criterion-Specific Fix Guidance

- **GitHub Actions rollback workflow**: Create a `rollback.yml` workflow triggered by `workflow_dispatch` that redeploys the previous release. Use `gh release list --limit 2` to identify the prior version, then trigger the deployment workflow for that version.
- **Kubernetes rollback**: Use `kubectl rollout undo deployment/<name>` for immediate rollback. Document this command and automate it via a script or CI workflow. For Argo Rollouts, use `kubectl argo rollouts abort <rollout-name>` or configure automatic rollback on analysis failure.
- **Container-based rollback**: If deploying Docker images, rollback means redeploying the previous image tag. Store the previous tag as a CI artifact or in a deployment log, and create a workflow that redeploys it.
- **Platform-specific rollback**: Vercel: `vercel rollback`. Heroku: `heroku releases:rollback`. AWS ECS: update service to previous task definition. Cloud Run: `gcloud run services update-traffic --to-revisions=PREVIOUS=100`.
- **Database-aware rollback**: If the deployment includes database migrations, ensure migrations are backward-compatible (expand-then-contract pattern) so rollback does not break the schema. Document rollback procedures for stateful changes separately.
- **Runbook documentation**: At minimum, create a `RUNBOOK.md` or a "Rollback" section in `DEPLOYMENT.md` documenting the exact rollback steps for each service. Include commands, expected output, and verification steps.
- **Automated rollback triggers**: Configure monitoring alerts (Datadog, PagerDuty, Grafana) that automatically trigger a rollback workflow via webhook when error rates spike post-deploy.

## Criterion-Specific Exploration Steps

- Look for rollback workflows: `grep -rl 'rollback\|rollout undo' .github/workflows/`
- Check for deployment documentation: `RUNBOOK.md`, `DEPLOYMENT.md`, `docs/rollback.md`
- Look for Argo Rollouts with automatic rollback analysis: `grep -r 'abortOnFailure\|rollbackOnFailure' k8s/ manifests/`
- Check if the deployment platform supports one-click rollback (Vercel, Heroku, etc.)
- Review recent deployment workflows for rollback steps or manual approval gates

## Criterion-Specific Verification Steps

- Confirm at least one rollback mechanism exists: a rollback workflow, documented rollback commands, or platform-native rollback capability
- Verify the rollback procedure can be executed without deep system knowledge (should be a single command or button press)
- If using Kubernetes, verify `kubectl rollout history deployment/<name>` shows multiple revisions available for rollback
