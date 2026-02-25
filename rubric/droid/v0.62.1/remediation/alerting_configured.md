---
signal_name: Alerting Configured
---

## Criterion-Specific Fix Guidance

- **PagerDuty integration**: Create a PagerDuty service for the application. Integrate with your monitoring tool (Datadog, Prometheus/Alertmanager, CloudWatch) by configuring the PagerDuty Events API v2 integration key. Define escalation policies with on-call rotations. Document the integration key in a secrets manager, not in code.
- **OpsGenie integration**: Create an OpsGenie team and configure alert routing rules. Add an API integration in OpsGenie and connect it to your monitoring backend. Define priority levels (P1-P5) and matching notification policies (P1 = page immediately, P3 = Slack notification only).
- **Prometheus Alertmanager**: Create alerting rules in a `prometheus/alerts.yml` or `monitoring/alerting-rules.yml` file. Define rules using PromQL: `alert: HighErrorRate; expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05; for: 5m; labels: { severity: critical }`. Configure Alertmanager receivers (PagerDuty, Slack, email) in `alertmanager.yml`.
- **Datadog Monitors**: Define monitors as code using Terraform (`datadog_monitor` resource) or Datadog's API. Store monitor definitions in `monitoring/datadog/` directory. At minimum, create monitors for: error rate spike, latency p99 above threshold, and service downtime.
- **CloudWatch Alarms**: Create CloudWatch alarms via Terraform, CDK, or CloudFormation. Define alarm actions that trigger SNS topics connected to PagerDuty/OpsGenie. Example: `aws cloudwatch put-metric-alarm --alarm-name high-error-rate --metric-name 5XXError --threshold 10 --comparison-operator GreaterThanThreshold`.
- **Slack alerting**: At minimum, configure critical alerts to post to a dedicated `#alerts-<service-name>` Slack channel. Use Slack webhooks from Alertmanager, Datadog, or a custom integration. Slack alone is insufficient for critical alerts (use PagerDuty/OpsGenie for paging).
- **Alert as code**: Store all alert definitions in the repository (Terraform, YAML, or JSON). This ensures alerts are version-controlled, reviewed in PRs, and reproducible across environments.
- **Runbooks**: Link each alert to a runbook document explaining what the alert means, how to investigate, and common remediation steps. Add `annotations: { runbook_url: "..." }` in Prometheus rules or `message` in Datadog monitors.

## Criterion-Specific Exploration Steps

- Search for alert configuration files: `grep -rn 'alert:\|alerting\|monitor\|alarm' monitoring/ prometheus/ terraform/ --include='*.yml' --include='*.yaml' --include='*.tf'`
- Check for PagerDuty/OpsGenie integration: `grep -rn 'pagerduty\|opsgenie\|PAGERDUTY_SERVICE_KEY\|OPSGENIE_API_KEY' .env* terraform/ monitoring/`
- Look for Alertmanager configuration: `alertmanager.yml`, `alertmanager.yaml`
- Check Terraform for monitoring resources: `grep -rn 'datadog_monitor\|aws_cloudwatch_metric_alarm\|opsgenie_alert_policy' terraform/`
- Look for Slack webhook configurations: `grep -rn 'slack_webhook\|incoming-webhook\|SLACK_ALERT' monitoring/ terraform/ .env*`
- Check for alert definitions in CI/CD configs or deployment manifests

## Criterion-Specific Verification Steps

- Confirm at least one alerting rule or monitor is defined in the repository (not just in a SaaS dashboard with no code representation)
- Verify alerts have a notification target (PagerDuty, OpsGenie, Slack, or email) -- an alert rule with no receiver is ineffective
- Check that critical alerts (P1/P2) route to a paging service (PagerDuty/OpsGenie), not just Slack
- Verify alert thresholds are reasonable (not set so high they never fire, or so low they cause alert fatigue)
- Confirm alert definitions are committed to version control and applied via CI/CD or Terraform
