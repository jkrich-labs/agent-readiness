---
signal_name: Metrics Collection
---

## Criterion-Specific Fix Guidance

- **Prometheus (Python)**: Install `prometheus-client` (`pip install prometheus-client`). Create metrics in your application: `from prometheus_client import Counter, Histogram; REQUEST_COUNT = Counter('http_requests_total', 'Total requests', ['method', 'endpoint', 'status'])`. Expose a `/metrics` endpoint using `start_http_server(8000)` or integrate with your framework (e.g., `prometheus-fastapi-instrumentator` for FastAPI).
- **Prometheus (TypeScript/JavaScript)**: Install `prom-client` (`npm install prom-client`). Initialize default metrics: `import { collectDefaultMetrics, register } from 'prom-client'; collectDefaultMetrics();`. Add a `/metrics` route: `app.get('/metrics', async (req, res) => { res.set('Content-Type', register.contentType); res.end(await register.metrics()); })`.
- **Datadog**: Install the Datadog agent and client library (`ddtrace` for Python, `dd-trace` for Node.js). Use `dogstatsd` for custom metrics: `from datadog import statsd; statsd.increment('page.views')`. Configure via `DD_AGENT_HOST` and `DD_DOGSTATSD_PORT` environment variables.
- **OpenTelemetry Metrics**: Use `@opentelemetry/sdk-metrics` (Node.js) or `opentelemetry-sdk` (Python) to create meters and instruments (counters, histograms, gauges). Export to Prometheus, Datadog, or any OTLP-compatible backend.
- **CloudWatch (AWS)**: Use `aws-sdk` / `boto3` to push custom metrics via `put_metric_data`. For ECS/Lambda, enable container insights or Lambda Insights for automatic infrastructure metrics.
- **New Relic**: Install the agent (`newrelic` npm package or `newrelic` pip package). Configure with `NEW_RELIC_LICENSE_KEY` and `NEW_RELIC_APP_NAME`. The agent auto-instruments common frameworks.
- **Key metrics to track**: At minimum, track request rate (requests/second), error rate (5xx responses), and latency (p50, p95, p99). These are the RED metrics (Rate, Errors, Duration) essential for service monitoring.
- **Dashboard creation**: Define dashboards as code using Grafana JSON models, Datadog dashboard JSON, or Terraform `datadog_dashboard` resources. Store in `monitoring/dashboards/` and apply via CI.

## Criterion-Specific Exploration Steps

- Check dependencies for metrics libraries: `grep -E 'prometheus-client|prom-client|datadog|ddtrace|dd-trace|newrelic|@opentelemetry/sdk-metrics' pyproject.toml package.json`
- Search for metrics initialization: `grep -rn 'Counter\|Histogram\|Gauge\|collectDefaultMetrics\|statsd\|CloudWatch' src/`
- Look for a `/metrics` endpoint in route definitions
- Check for Datadog agent configuration: `datadog.yaml`, `DD_AGENT_HOST` in env files
- Check for New Relic configuration: `newrelic.ini`, `newrelic.js`, `NEW_RELIC_LICENSE_KEY` in env
- Look for CloudWatch metric calls: `grep -rn 'put_metric_data\|PutMetricData\|cloudwatch' src/`
- Check Terraform/IaC for monitoring resource definitions

## Criterion-Specific Verification Steps

- Confirm a metrics library is in project dependencies and initialized in application code
- For Prometheus, start the app and verify `/metrics` returns valid Prometheus exposition format: `curl localhost:8000/metrics`
- For Datadog/New Relic, confirm the agent configuration file exists and required environment variables are documented
- Verify at least one custom application metric is defined (not just default runtime metrics)
- Check that metrics include appropriate labels/tags for meaningful aggregation (e.g., endpoint, status code, method)
