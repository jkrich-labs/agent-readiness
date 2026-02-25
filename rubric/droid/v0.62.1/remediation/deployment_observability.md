---
signal_name: Deployment Observability
---

## Criterion-Specific Fix Guidance

- **Monitoring dashboard links in docs**: Add a `## Monitoring` or `## Observability` section to the project `README.md` or a dedicated `docs/runbook.md` that includes direct links to Grafana dashboards, Datadog dashboards, or CloudWatch consoles for the service. Include links for key views: service overview, error rate, latency, and resource utilization.
- **Deploy notification to Slack/Teams**: Configure deployment pipelines to post notifications to a `#deploys` or `#releases` channel. In GitHub Actions, add a step using `slackapi/slack-github-action` to send a message with commit SHA, deployer, environment, and a link to the deployment logs. Example payload: `{ "text": "Deployed my-service@abc1234 to production by @user" }`.
- **Datadog deployment tracking**: Use Datadog's Deployment Tracking feature by sending deployment events via the API or `datadog-ci`: `datadog-ci deployment mark --env production --service my-service --revision $GIT_SHA`. This overlays deploy markers on dashboards for correlation.
- **Grafana annotations**: Post deploy annotations to Grafana via the API: `curl -X POST grafana/api/annotations -d '{"tags":["deploy"],"text":"v1.2.3 deployed"}'`. These appear as vertical lines on dashboard graphs, making it easy to correlate deployments with metric changes.
- **GitHub Deployments API**: Use the GitHub Deployments API to create deployment records: `gh api repos/{owner}/{repo}/deployments -f ref=$SHA -f environment=production`. This enables deployment status tracking in the GitHub UI and integrates with third-party tools.
- **Sentry release tracking**: Notify Sentry of new releases so errors can be attributed to specific deployments: `sentry-cli releases new VERSION && sentry-cli releases set-commits VERSION --auto && sentry-cli releases finalize VERSION`. Add `sentry-cli releases deploys VERSION new -e production` to mark the deployment.
- **Post-deploy health check**: Add a CI step that waits 2-5 minutes after deployment and checks key health metrics. If error rate spikes above a threshold, automatically trigger a rollback or alert the team.

## Criterion-Specific Exploration Steps

- Check README.md and docs/ for monitoring or observability links: `grep -rn 'grafana\|datadog\|dashboard\|cloudwatch\|monitoring' README.md docs/`
- Look for deploy notification steps in CI/CD: `grep -rn 'slack\|notify\|deploy.*notification\|deployment.*mark' .github/workflows/ .circleci/ Jenkinsfile`
- Search for Sentry release integration: `grep -rn 'sentry-cli releases\|SENTRY_RELEASE' .github/workflows/ Makefile`
- Check for Grafana annotation or Datadog event API calls in deploy scripts
- Look for GitHub Deployments API usage: `grep -rn 'deployments\|deployment_status' .github/workflows/`
- Check for post-deploy verification steps in pipelines

## Criterion-Specific Verification Steps

- Confirm monitoring dashboard links are documented and accessible (click them to verify they resolve)
- Trigger a deployment (or simulate one in a staging environment) and verify a notification appears in the configured channel
- Check that deploy events appear on monitoring dashboards as annotations or markers
- Verify that Sentry (if used) shows release information and can attribute errors to specific releases
- Confirm the deployment notification includes useful context: commit SHA, environment, deployer, and a link to logs or the PR
