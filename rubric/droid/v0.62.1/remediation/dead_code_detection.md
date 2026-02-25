---
signal_name: Dead Code Detection
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Install `knip` (`npm install -D knip`) and add a script to `package.json`: `"knip": "knip"`. Knip detects unused files, dependencies, exports, and types. Configure via `knip.json` or `knip.ts` if you need to exclude specific entry points or workspaces. Alternative: use `ts-prune` (`npm install -D ts-prune`) to find unused TypeScript exports.
- **Python projects**: Install `vulture` (`pip install vulture`) and run `vulture . --min-confidence 80` to find unused code. Add a `vulture` whitelist file for intentional unused code (e.g., framework callbacks). Configure in `pyproject.toml` under `[tool.vulture]`: `min_confidence = 80`, `paths = ["src"]`.
- **Go projects**: Use `staticcheck` (part of the standard Go toolchain via `go install honnef.co/go/tools/cmd/staticcheck@latest`). The `U1000` check detects unused code. Run `staticcheck ./...`.
- **SonarQube alternative**: If SonarQube is configured, it detects dead code automatically. Verify the quality profile includes rules for unused code (e.g., `typescript:S1172` for unused parameters, `python:S1144` for unused private methods).
- Add dead code detection to CI as a step that runs after tests. This ensures new dead code is caught before merging.
- Create an ignore list or baseline for existing dead code and enforce zero new dead code additions.

## Criterion-Specific Exploration Steps

- Check `package.json` for `knip` or `ts-prune` in `devDependencies` and related scripts
- Check for `knip.json`, `knip.ts`, or `knip` config in `package.json`
- Check Python dev dependencies for `vulture`
- Check `pyproject.toml` for `[tool.vulture]` section
- Look for `.golangci.yml` with `unused` or `staticcheck` linter enabled
- Check CI workflows for dead code detection steps
- Check for `sonar-project.properties` or SonarQube quality profile configuration

## Criterion-Specific Verification Steps

- **TypeScript/JavaScript**: Run `npx knip` and confirm it executes and produces a report (even if it finds unused code, the tool itself should work)
- **Python**: Run `vulture . --min-confidence 80` and confirm it executes without errors
- **Go**: Run `staticcheck ./...` and confirm it includes unused code checks
- Verify the tool is configured in CI, not just installed locally
