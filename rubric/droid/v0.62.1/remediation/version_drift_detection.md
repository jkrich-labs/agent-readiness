---
signal_name: Version Drift Detection
---

## Criterion-Specific Fix Guidance

- **syncpack**: Install `syncpack` (`npm install --save-dev syncpack`) for monorepos using npm/yarn/pnpm workspaces. It ensures consistent dependency versions across packages. Add to CI: `npx syncpack list-mismatches` (fails if versions drift). Configure in `.syncpackrc.json` with version groups and policies.
- **manypkg**: Install `@manypkg/cli` (`npm install --save-dev @manypkg/cli`). Run `npx manypkg check` to find version mismatches across workspace packages. Add to CI as a check step. Run `npx manypkg fix` to auto-fix mismatches.
- **Renovate version grouping**: Configure Renovate (`renovate.json`) to group related dependency updates. Use `"packageRules"` to group packages by ecosystem or team ownership. Example: `{"matchPackagePatterns": ["^@typescript-eslint/"], "groupName": "typescript-eslint"}`. This prevents packages from drifting when one is updated but related ones are not.
- **Dependabot grouping**: In `.github/dependabot.yml`, use `groups` to batch related dependency updates together. Example: group all `@testing-library/*` packages into a single PR.
- **Custom CI check**: Write a script that extracts dependency versions from all `package.json` files in the monorepo and reports mismatches. Fail CI if shared dependencies have conflicting version ranges.
- **Go**: Use `go mod tidy` in each module and verify `go.sum` consistency. In a Go workspace (`go.work`), ensure modules use compatible dependency versions.
- **Python**: In a monorepo with multiple `pyproject.toml` files, write a script that checks shared dependency version specifiers are compatible.

## Criterion-Specific Exploration Steps

- Check for version management tools: `syncpack` or `@manypkg/cli` in root `package.json` devDependencies
- Check for `.syncpackrc*` or `manypkg` configuration
- Look at `renovate.json` or `.github/dependabot.yml` for grouping rules
- Compare dependency versions across workspace packages: `npx syncpack list-mismatches` or manually inspect multiple `package.json` files
- Check CI workflows for version consistency checks

## Criterion-Specific Verification Steps

- Run `npx syncpack list-mismatches` and confirm zero mismatches (or only expected intentional differences)
- Confirm version drift detection is integrated into CI (either as a check step or via Renovate/Dependabot grouping config)
- Verify that Renovate or Dependabot is configured with package grouping rules if used as the drift detection mechanism
