---
signal_name: Deployment Frequency
---

## Criterion-Specific Fix Guidance

- **Target**: Multiple deployments per week (at minimum 2-3 per week for Level 4).
- **Automated CD pipeline**: Set up continuous deployment from the `main` branch. Use GitHub Actions with deployment triggers on push to `main` or on release creation. Platforms: Vercel, Netlify, AWS CodeDeploy, Google Cloud Deploy, Heroku, Fly.io, Railway.
- **GitHub Releases**: Create releases using `gh release create` or automate via semantic-release. Each release should trigger a deployment workflow. This also provides a measurable audit trail.
- **Reduce batch size**: Deploy smaller changes more frequently rather than large batch releases. Smaller deployments reduce risk and increase deployment frequency naturally.
- **Feature flags**: Use feature flags (LaunchDarkly, Statsig, Unleash) to decouple deployment from feature release. This allows deploying incomplete features behind flags without waiting.
- **Trunk-based development**: Adopt short-lived feature branches (< 1 day) merged frequently to `main`. This naturally increases deployment cadence.
- **GitHub Actions deployment workflow**: Create `.github/workflows/deploy.yml` triggered on push to `main` or `workflow_dispatch` for manual deploys. Include environment protection rules for production.
- **Measure via DORA metrics**: Use `gh run list --workflow=deploy.yml --limit 20 --json createdAt` to track deployment frequency over time.

## Criterion-Specific Exploration Steps

- Check deployment frequency: `gh release list --limit 20` to see release cadence
- Check CI/CD workflows: `gh run list --limit 20 --json workflowName,createdAt,conclusion` to identify deployment runs
- Look for deployment workflows in `.github/workflows/` that deploy to production
- Check for CD platform configuration: `vercel.json`, `netlify.toml`, `fly.toml`, `app.yaml`, `Procfile`, `render.yaml`
- Review the release cadence: are there multiple releases per week?

## Criterion-Specific Verification Steps

- Run `gh release list --limit 10` and verify there are multiple releases within recent weeks
- Run `gh run list --workflow=<deploy-workflow> --limit 10 --json createdAt` and confirm multiple runs per week
- Check the deploy workflow exists and has been executed recently
