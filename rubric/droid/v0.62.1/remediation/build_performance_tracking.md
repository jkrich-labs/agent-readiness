---
signal_name: Build Performance Tracking
---

## Criterion-Specific Fix Guidance

- **Measure build duration in CI**: Add timing to build steps. In GitHub Actions, wrap build commands with `time` or use `date` before/after. Use job summaries (`$GITHUB_STEP_SUMMARY`) to report durations.
- **Export metrics**: Send build duration metrics to a monitoring system (Datadog, Grafana, Prometheus). Use CI environment variables (`GITHUB_RUN_ID`, timestamps) to compute and export metrics via a post-build step.
- **Configure build caching**: Enable caching in the build tool. For Turborepo: `turbo.json` with `"cache": true` and remote caching via Vercel. For Nx: `nx.json` with `"tasksRunnerOptions": {"default": {"runner": "@nrwl/nx-cloud"}}`. For Gradle: enable build cache in `gradle.properties` (`org.gradle.caching=true`).
- **Python projects**: Use `uv` (has built-in caching) instead of `pip`. Cache `.uv/cache` in CI. For build timing, wrap commands: `time uv sync && time uv run pytest`.
- **Node.js projects**: Use `npm ci` with `actions/cache` for `node_modules` or `~/.npm`. For bundler performance, configure webpack's `cache: { type: 'filesystem' }` or use `vite` which caches by default.
- **Track trends**: Use GitHub Actions job summaries or a dedicated dashboard to track build times over weeks. Alert when build duration regresses by more than 20%.
- **Dedicated tools**: Consider BuildPulse, Datadog CI Visibility, or Honeycomb for build performance observability.

## Criterion-Specific Exploration Steps

- Check CI workflows for timing commands, caching steps, or metrics export
- Look for build caching config: `turbo.json`, `nx.json`, `gradle.properties`, webpack/vite cache settings
- Search for CI analytics integrations: Datadog, BuildPulse, Honeycomb config in workflows
- Check for `$GITHUB_STEP_SUMMARY` usage in workflows (indicates CI reporting)
- Look for `actions/cache` usage and what directories are cached

## Criterion-Specific Verification Steps

- Confirm at least one mechanism exists: build duration is measured in CI output, caching is configured, or metrics are exported to an external system
- Check recent CI runs for timing data in logs or job summaries
- Verify cache hit rates by checking CI logs for "cache hit" or "cache restored" messages
