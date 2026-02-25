---
signal_name: Monorepo Tooling
---

## Criterion-Specific Fix Guidance

- **npm workspaces**: Add `"workspaces": ["packages/*", "apps/*"]` to the root `package.json`. Each sub-package gets its own `package.json`. Install shared dependencies at the root, package-specific ones in each workspace. Run commands across workspaces with `npm run --workspaces <script>`.
- **yarn workspaces**: Add `"workspaces": ["packages/*"]` to root `package.json`. Yarn automatically hoists shared dependencies. Use `yarn workspace <name> <command>` to target specific packages.
- **pnpm workspaces**: Create `pnpm-workspace.yaml` at the repo root with `packages: ['packages/*', 'apps/*']`. pnpm's strict node_modules structure prevents phantom dependencies. Use `pnpm --filter <package> <command>`.
- **Turborepo**: Install (`npm install turbo --save-dev`) and create `turbo.json` defining the task pipeline (build, test, lint) with dependency relationships. Enables intelligent caching and parallel execution. Example: `{"pipeline": {"build": {"dependsOn": ["^build"]}, "test": {"dependsOn": ["build"]}}}`.
- **Nx**: Initialize with `npx nx init`. Creates `nx.json` with task runner config. Provides `nx affected` for incremental builds, computation caching, and project graph visualization.
- **Go workspaces**: Create `go.work` at the repo root with `go work init ./service-a ./service-b`. Enables multi-module development.
- **Cargo workspaces**: Add `[workspace]` section to root `Cargo.toml` with `members = ["crates/*"]`. Shared dependency resolution across crates.
- **Lerna** (legacy): `npx lerna init`. Manages versioning and publishing for JS monorepos. Often combined with npm/yarn workspaces for dependency management.

## Criterion-Specific Exploration Steps

- Check for workspace config: `workspaces` field in root `package.json`, `pnpm-workspace.yaml`, `go.work`, `[workspace]` in `Cargo.toml`
- Look for monorepo build tools: `turbo.json`, `nx.json`, `lerna.json`
- Check the repo structure for multiple apps/packages: `ls apps/ packages/ services/ crates/ modules/ 2>/dev/null`
- Determine if this is actually a monorepo (multiple independently deployable units) or a single-app repo (monorepo tooling may not be needed)

## Criterion-Specific Verification Steps

- Confirm workspace configuration exists and lists the correct package directories
- Run the workspace-aware install command (`npm install`, `pnpm install`) and verify it resolves cross-workspace dependencies
- If using Turborepo/Nx, verify task caching works: run `turbo run build` twice and confirm the second run uses cache
