---
signal_name: Fast CI Feedback
---

## Criterion-Specific Fix Guidance

- **Target**: Average CI duration under 10 minutes from push to green/red status.
- **Parallelise test suites**: Split tests across multiple CI jobs using matrix strategies. In GitHub Actions, use `strategy: matrix:` to run test shards in parallel. Tools like `pytest-split`, `jest --shard`, or `go test -parallel` help distribute work.
- **Cache dependencies aggressively**: Use `actions/cache` or the built-in cache for `actions/setup-node`, `actions/setup-python`, etc. Cache `node_modules`, `.pnpm-store`, `.uv/cache`, `~/.cache/pip`, `~/.cargo/registry`, and `~/go/pkg/mod`.
- **Use faster runners**: Switch to larger GitHub-hosted runners (`runs-on: ubuntu-latest-xl`) or self-hosted runners with more CPU/RAM. Consider ARM runners if your stack supports them.
- **Avoid redundant work**: Use path filters (`on: push: paths:`) to skip CI for documentation-only changes. Use `actions/changed-files` to run only affected test suites.
- **Optimize Docker builds**: Use multi-stage builds, layer caching (`docker/build-push-action` with `cache-from`), and avoid installing dev dependencies in production images.
- **Trim the test suite**: Move slow integration tests to a separate workflow that runs on `main` merge only. Keep the PR check suite focused on unit and fast integration tests.
- **Incremental builds**: Use tools like Turborepo (`turbo run build --filter=...[HEAD^]`), Nx (`nx affected:test`), or Bazel for incremental builds that skip unchanged packages.

## Criterion-Specific Exploration Steps

- Check recent CI run durations: `gh run list --limit 10 --json databaseId,conclusion,createdAt,updatedAt` and compute elapsed times
- Check for caching in CI workflows: search for `actions/cache` or `cache:` keys in `.github/workflows/*.yml`
- Look at the workflow structure: count the number of jobs, check for matrix strategies
- Identify the slowest steps by reviewing CI logs: `gh run view <run-id> --log`
- Check if path filters are used: look for `paths:` or `paths-ignore:` in workflow triggers

## Criterion-Specific Verification Steps

- Measure CI duration for the 5 most recent runs: `gh run list --limit 5 --json databaseId,createdAt,updatedAt` and compute the average duration
- Confirm the average is under 10 minutes
- After optimizations, push a small change and time the resulting CI run
