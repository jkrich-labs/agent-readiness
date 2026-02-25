---
signal_name: Test Isolation
---

## Criterion-Specific Fix Guidance

- **Python (pytest-xdist)**: Install `pytest-xdist` (`pip install pytest-xdist` or add to `pyproject.toml` dev dependencies). Run tests in parallel with `pytest -n auto` (auto-detects CPU count) or `pytest -n 4` for a fixed worker count. Add `addopts = "-n auto"` to `pyproject.toml` `[tool.pytest.ini_options]` to make parallel the default.
- **TypeScript/JavaScript (Jest)**: Jest runs test files in parallel by default via worker processes. Ensure `--runInBand` is NOT set in CI scripts or `jest.config.*`. For explicit parallel control, set `maxWorkers` in `jest.config.ts`: `maxWorkers: '50%'` or `maxWorkers: 4`.
- **Go**: Add `t.Parallel()` as the first line inside each `Test*` function and each subtest created with `t.Run()`. Run with `go test -parallel 8 ./...` to control concurrency. Ensure tests do not share mutable package-level state.
- **Eliminate shared state**: Each test must manage its own fixtures. Use `tmp_path` (pytest), `t.TempDir()` (Go), or `jest`'s `beforeEach` to create isolated state. Replace shared database connections with per-test containers using `testcontainers` (available for Python, Node.js, Go, Java).
- **Testcontainers**: For integration tests that need databases, install `testcontainers` (`pip install testcontainers` / `npm install testcontainers`) and spin up a fresh container per test suite. This ensures complete isolation and deterministic results.
- **Avoid global fixtures**: Replace module-level setup that mutates shared state with function-scoped or test-scoped fixtures. In pytest, prefer `@pytest.fixture(scope="function")` over `scope="session"` for mutable resources.
- **CI configuration**: Set parallel workers in CI workflow explicitly: `pytest -n auto --dist worksteal` for pytest-xdist, or `jest --maxWorkers=2` for memory-constrained CI runners.

## Criterion-Specific Exploration Steps

- Check `pyproject.toml`, `setup.cfg`, or `pytest.ini` for existing pytest-xdist configuration (`addopts` containing `-n`)
- Check `package.json` devDependencies and `jest.config.*` for Jest worker configuration
- Search for `testcontainers` in dependency files: `grep -r 'testcontainers' pyproject.toml package.json go.mod`
- Look for `t.Parallel()` calls in Go test files: `grep -rn 't.Parallel()' --include='*_test.go'`
- Check if `--runInBand` is used in any npm scripts or CI steps (this disables Jest parallelism)
- Look for shared mutable state patterns: module-level variables modified in tests, shared database fixtures with `scope="session"`

## Criterion-Specific Verification Steps

- Run `pytest -n auto -v` and confirm output shows multiple workers (e.g., `[gw0]`, `[gw1]` prefixes in output)
- Run `jest --verbose` and confirm tests from different files run concurrently (check timing output)
- For Go, run `go test -v -parallel 4 ./...` and confirm tests execute concurrently
- Verify no test ordering dependencies: run `pytest --randomly-seed=12345` (with `pytest-randomly`) or `jest --randomize` to confirm tests pass in any order
- Check that CI logs show parallel execution rather than serial
