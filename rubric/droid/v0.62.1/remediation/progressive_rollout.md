---
signal_name: Progressive Rollout
---

## Criterion-Specific Fix Guidance

- **Canary deployments**: Deploy new versions to a small subset of servers/pods first (e.g., 5%), monitor for errors, then gradually increase to 100%. Configure in Kubernetes with Argo Rollouts (`apiVersion: argoproj.io/v1alpha1`, `kind: Rollout`) or Flagger. AWS: use CodeDeploy with `CodeDeployDefault.OneAtATime` or percentage-based config.
- **Percentage-based rollouts**: Use feature flags (LaunchDarkly, Statsig) to expose new features to a percentage of users. Start at 1-5%, monitor metrics, then ramp to 25%, 50%, 100%. This decouples deployment from feature release.
- **Ring deployments**: Define deployment rings (internal users -> beta users -> 10% production -> 100% production). Document the ring progression criteria (error rate, latency thresholds) and automate advancement between rings.
- **Kubernetes**: Use Argo Rollouts with a `canary` strategy specifying steps: `setWeight: 5`, `pause: {duration: 10m}`, `setWeight: 25`, etc. Or use Istio traffic splitting with `VirtualService` weight-based routing.
- **Serverless/PaaS**: Vercel and Netlify support preview deployments. AWS Lambda supports weighted aliases. Cloud Run supports traffic splitting between revisions.
- **Monitoring gates**: Configure automated rollback triggers based on error rate, latency P99, or custom metrics. Argo Rollouts supports `analysis` templates that query Prometheus/Datadog and abort on threshold violations.
- **Documentation**: At minimum, document the rollout strategy in a `DEPLOYMENT.md` or in the README's deployment section, describing how new versions are gradually rolled out.

## Criterion-Specific Exploration Steps

- Check for Argo Rollouts manifests: `grep -r 'argoproj.io/v1alpha1' k8s/ manifests/ deploy/`
- Look for Flagger configuration: `flagger.yaml`, `canary.yaml` in Kubernetes manifests
- Search for traffic splitting config: Istio `VirtualService`, AWS CodeDeploy `appspec.yml`, Cloud Run traffic config
- Check feature flag configs for percentage-based targeting rules
- Look for deployment documentation: `DEPLOYMENT.md`, deployment section in README
- Check CI/CD workflows for staged deployment steps (deploy to staging, then production)

## Criterion-Specific Verification Steps

- Confirm at least one progressive rollout mechanism is configured: canary deployment tooling, percentage-based feature flags, or documented ring deployment process
- If using Argo Rollouts, verify the Rollout resource has a `canary` strategy with weight steps
- If using feature flags, verify at least one flag uses percentage-based targeting
