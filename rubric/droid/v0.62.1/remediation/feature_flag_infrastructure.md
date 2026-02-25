---
signal_name: Feature Flag Infrastructure
---

## Criterion-Specific Fix Guidance

- **LaunchDarkly**: Install the SDK (`npm install launchdarkly-node-server-sdk` or `pip install launchdarkly-server-sdk`). Initialize the client with an SDK key and wrap feature code in `ld_client.variation('flag-key', user, default_value)` calls. Configuration typically lives in environment variables.
- **Statsig**: Install the SDK (`npm install statsig-node` or `pip install statsig`). Initialize with `Statsig.initialize(server_secret)` and check gates with `Statsig.checkGate(user, 'gate_name')`.
- **Unleash**: Self-hosted option. Install the SDK (`npm install unleash-client` or `pip install UnleashClient`). Configure the Unleash server URL and API token. Check flags with `unleash.isEnabled('feature-name')`.
- **GrowthBook**: Install the SDK (`npm install @growthbook/growthbook` or `pip install growthbook`). Provides both feature flags and A/B testing. Configure via JSON features file or API.
- **Custom implementation**: Create a simple feature flag module that reads flags from environment variables, a JSON config file, or a database. Minimum viable: a `feature_flags.json` file with `{"flag_name": true/false}` and a helper function to check flags.
- **Best practices**: Centralize flag checks through a single module/service. Use typed flag definitions. Set sensible defaults for when the flag service is unavailable. Log flag evaluations for debugging.
- **Environment-based flags**: At minimum, use environment variables as feature flags (e.g., `FEATURE_NEW_CHECKOUT=true`) with a helper module that reads and caches them.

## Criterion-Specific Exploration Steps

- Search for feature flag SDK imports: `grep -r 'launchdarkly\|statsig\|unleash\|growthbook\|feature.flag\|feature_flag' src/ lib/ app/`
- Check `package.json` or `pyproject.toml` for feature flag SDK dependencies
- Look for feature flag configuration files: `flags.json`, `features.json`, `.launchdarkly/`, `growthbook.json`
- Search for environment variable patterns that look like feature flags: `grep -r 'FEATURE_\|FF_\|FLAG_' src/ .env.example`
- Check for a custom feature flag module or service

## Criterion-Specific Verification Steps

- Confirm a feature flag SDK is installed as a dependency, OR a custom feature flag module/config exists
- Verify feature flags are actually used in application code (not just installed but unused)
- Check that flag evaluation has a sensible default/fallback when the flag service is unreachable
