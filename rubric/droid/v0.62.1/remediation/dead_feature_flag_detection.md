---
signal_name: Dead Feature Flag Detection
---

## Criterion-Specific Fix Guidance

- **LaunchDarkly code references**: Install the LaunchDarkly code references tool (`ld-find-code-refs`). Add it to CI with a GitHub Action: `launchdarkly/find-code-references`. It scans your codebase for flag key references and reports them to LaunchDarkly, which can then identify stale flags that no longer appear in code.
- **Custom CI script**: Write a script that extracts all feature flag keys from the flag management system (via API) and searches the codebase for each key. Flags that exist in the management system but have zero code references are candidates for removal. Run this weekly or on each merge to `main`.
- **Grep-based detection**: Maintain a list of known flag keys in a config file (`feature-flags.json`). Add a CI step that checks each flag key appears in at least one source file. Alert or fail if a flag key has no references.
- **Flag lifecycle management**: Establish a process where every feature flag has an expiration date or TTL. Use a tracking document or issue template that requires setting a removal date when creating a flag. Schedule periodic reviews (e.g., monthly) to clean up expired flags.
- **Statsig/GrowthBook stale detection**: Both platforms have built-in stale flag detection. Enable email alerts for flags that have been fully rolled out for more than 30 days.
- **Automated cleanup PRs**: Create a CI workflow that runs monthly, identifies flags that have been 100% rolled out for > N days, and opens a PR removing the flag checks from code, replacing them with the winning variant.
- **Lint rule**: Create a custom ESLint or Ruff rule that flags hardcoded `true`/`false` values in feature flag check calls (indicating a flag that should be cleaned up).

## Criterion-Specific Exploration Steps

- Search for LaunchDarkly code refs action: `grep -r 'find-code-references\|ld-find-code-refs' .github/workflows/`
- Check for feature flag inventory files: `feature-flags.json`, `flags.yaml`, or similar manifest
- Look for stale flag detection scripts in `scripts/` or CI workflows
- Check the feature flag management dashboard for flags that are 100% rolled out or archived
- Search for flag references in code and note any that appear to be permanently `true` or `false`

## Criterion-Specific Verification Steps

- Confirm at least one stale flag detection mechanism exists: LaunchDarkly code refs, a custom CI scanner, or a documented periodic review process
- If using `ld-find-code-refs`, verify it runs in CI and the LaunchDarkly dashboard shows code reference data
- Verify the detection mechanism has identified at least one stale flag (or confirms zero stale flags exist)
