---
signal_name: Unused Dependencies Detection
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Install `depcheck` (`npm install -D depcheck`) and add a script to `package.json`: `"depcheck": "depcheck"`. Run `npx depcheck` to find unused dependencies, missing dependencies, and unused devDependencies. Configure via `.depcheckrc.json` to ignore known false positives: `{ "ignorePatterns": ["dist"], "ignoreMatches": ["@types/*"] }`.
- **Python projects**: Install `deptry` (`pip install deptry`) and run `deptry .` to detect unused dependencies, missing dependencies, and transitive dependencies used directly. Configure in `pyproject.toml` under `[tool.deptry]` with `ignore_notebooks = true` and `per_rule_ignores` for known exceptions.
- **Go projects**: Run `go mod tidy` to remove unused dependencies from `go.mod` and `go.sum`. Add `go mod tidy && git diff --exit-code go.mod go.sum` to CI to ensure no unused dependencies are committed.
- **Rust projects**: Use `cargo-udeps` (`cargo install cargo-udeps && cargo +nightly udeps`). This finds unused dependencies in `Cargo.toml`.
- **Java/Maven projects**: Run `mvn dependency:analyze` to find unused declared dependencies and used undeclared dependencies.
- Add unused dependency detection to CI. For JS: `npx depcheck --skip-missing` exits non-zero if unused deps are found. For Python: `deptry .` exits non-zero on violations.
- Regularly audit and remove unused dependencies to reduce attack surface and install times.

## Criterion-Specific Exploration Steps

- Check `package.json` for `depcheck` in `devDependencies` and related scripts
- Check for `.depcheckrc`, `.depcheckrc.json`, or `.depcheckrc.yml` config files
- Check Python dev dependencies for `deptry`
- Check `pyproject.toml` for `[tool.deptry]` section
- Look for `go mod tidy` in CI workflows or Makefiles (Go projects)
- Check CI workflows for dependency audit steps
- Check for `cargo-udeps` usage in Rust CI workflows

## Criterion-Specific Verification Steps

- **TypeScript/JavaScript**: Run `npx depcheck` and confirm it executes and produces a report
- **Python**: Run `deptry .` and confirm it executes and reports findings
- **Go**: Run `go mod tidy` followed by `git diff --exit-code go.mod` to verify no changes needed
- Verify the tool is integrated into CI (not just installed locally) and can fail the build on unused dependencies
