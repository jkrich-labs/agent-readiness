---
signal_name: Tech Debt Tracking
---

## Criterion-Specific Fix Guidance

- **TODO/FIXME scanner in CI**: Add a CI step that scans for `TODO`, `FIXME`, `HACK`, and `XXX` comments and reports them. Use `grep -rn 'TODO\|FIXME\|HACK\|XXX' --include='*.py' --include='*.ts' --include='*.js' --include='*.go' --include='*.rs' src/` or a dedicated tool like `leasot` (`npx leasot '**/*.{ts,js,py}'`).
- **SonarQube SQALE**: If SonarQube is configured, enable the SQALE/technical debt module. Ensure `sonar-project.properties` is present and the quality profile tracks code smells and technical debt ratio.
- **Documented tracking system**: Maintain a `TECH_DEBT.md` file or use GitHub Issues with a `tech-debt` label. Document known debt items with severity and rough remediation effort.
- **Pre-commit integration**: Add `leasot` or a custom script as a pre-commit hook that warns (but does not block) when new TODO/FIXME comments are added without a linked issue number.
- **GitHub Actions example**: Add a step `run: npx leasot '**/*.{ts,js,tsx,jsx}' --reporter json > tech-debt-report.json` and upload as an artifact or post as a PR comment.
- **Python ecosystem**: Use `pylint` with the `fixme` checker enabled (`enable=fixme` in `.pylintrc` or `pyproject.toml`), or `ruff` rule `FIX` to detect fixme comments.

## Criterion-Specific Exploration Steps

- Search for existing TODO/FIXME comments: `grep -rn 'TODO\|FIXME' src/ lib/ app/` to gauge current debt
- Check CI workflows for any existing debt scanning steps
- Look for `sonar-project.properties` or `.sonarcloud.properties`
- Check if a `TECH_DEBT.md` or similar document exists
- Check GitHub Issues for a `tech-debt` label: `gh label list | grep -i debt`
- Look for `leasot` in `package.json` devDependencies

## Criterion-Specific Verification Steps

- Confirm at least one mechanism exists: CI scanner step, SonarQube config with SQALE enabled, or a `TECH_DEBT.md` with substantive content
- Run `npx leasot '**/*.{ts,js,py}'` locally and verify it produces output
- If using SonarQube, verify the project dashboard shows technical debt metrics
