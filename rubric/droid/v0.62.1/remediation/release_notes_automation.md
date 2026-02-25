---
signal_name: Release Notes Automation
---

## Criterion-Specific Fix Guidance

- **semantic-release**: Install and configure `semantic-release` (`npm install --save-dev semantic-release`). Create `.releaserc.json` or `release.config.js` with plugins for changelog generation and GitHub releases. Requires conventional commit messages (e.g., `feat:`, `fix:`, `chore:`). Add a CI step: `npx semantic-release`.
- **Changesets**: Install `@changesets/cli` (`npm install --save-dev @changesets/cli`). Run `npx changeset init` to set up. Developers add changesets with `npx changeset` before merging PRs. CI publishes with `npx changeset publish` and generates a CHANGELOG.
- **GitHub auto-generated release notes**: Configure `.github/release.yml` to categorize PRs by label. Then use `gh release create v1.0.0 --generate-notes` to auto-generate release notes from merged PRs.
- **release-please**: Google's release automation. Add `.release-please-manifest.json` and `release-please-config.json`. Use the `google-github-actions/release-please-action` in GitHub Actions. Automatically creates release PRs with changelogs.
- **Conventional Commits**: Adopt the Conventional Commits specification (`feat:`, `fix:`, `docs:`, `chore:`) as a prerequisite for automated changelog tools. Enforce via `commitlint` with a `commitlint.config.js` and a git hook or CI check.
- **Python projects**: Use `python-semantic-release` (`pip install python-semantic-release`). Configure in `pyproject.toml` under `[tool.semantic_release]`. Alternatively, maintain a `CHANGELOG.md` updated by a CI script that parses conventional commits.

## Criterion-Specific Exploration Steps

- Check for release automation config: `.releaserc*`, `release.config.*`, `.changeset/`, `.release-please-manifest.json`, `release-please-config.json`
- Check for `.github/release.yml` (GitHub auto-generated notes config)
- Look at `package.json` for `semantic-release`, `@changesets/cli`, or `standard-version` in devDependencies
- Check `pyproject.toml` for `[tool.semantic_release]` configuration
- Look at CI workflows for release/publish steps
- Check if `CHANGELOG.md` exists and appears to be auto-generated (has consistent formatting, dates, version headers)

## Criterion-Specific Verification Steps

- Confirm a release automation tool is configured and integrated into CI
- Check recent GitHub releases: `gh release list --limit 5` and verify they have substantive release notes (not empty)
- Verify the tool runs in CI: look for a release/publish job in workflow files that triggers on push to `main` or on tags
