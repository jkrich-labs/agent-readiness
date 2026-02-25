---
signal_name: Duplicate Code Detection
---

## Criterion-Specific Fix Guidance

- **Cross-language (preferred)**: Install `jscpd` (`npm install -g jscpd` or `npm install -D jscpd`). Create a `.jscpd.json` config file: `{ "threshold": 5, "reporters": ["console"], "ignore": ["**/node_modules/**", "**/__pycache__/**", "**/dist/**"] }`. Add a script to `package.json`: `"jscpd": "jscpd ./src"`. jscpd supports TypeScript, JavaScript, Python, Go, and many other languages.
- **Java/JVM projects**: Use PMD CPD (Copy-Paste Detector). Run `pmd cpd --minimum-tokens 100 --dir src/` or configure it in the Maven/Gradle build.
- **SonarQube alternative**: SonarQube detects duplicated code blocks automatically and reports duplication percentage. If the project uses SonarQube, verify the quality gate includes a duplication threshold (e.g., "Duplicated Lines (%)" < 3%).
- **Python-specific**: `pylint` has a `similarities` checker (enabled by default) that detects duplicate code. Configure minimum similarity lines in `.pylintrc` or `pyproject.toml`: `[tool.pylint.similarities]`, `min-similarity-lines = 6`.
- Add duplicate detection to CI. For jscpd: `jscpd ./src --threshold 5 --exitCode 1` will fail the build if duplication exceeds the threshold.
- Set a duplication threshold appropriate for the project (typically 3-5% for established codebases, stricter for new projects).

## Criterion-Specific Exploration Steps

- Check for `.jscpd.json` config file at the repo root
- Check `package.json` for `jscpd` in `devDependencies` or `dependencies`
- Check for PMD configuration files (`pmd-ruleset.xml`, `.pmd`) for Java projects
- Check `sonar-project.properties` for SonarQube integration
- Check `pyproject.toml` for `[tool.pylint.similarities]` or pylint similarity settings
- Search CI workflows for `jscpd`, `pmd cpd`, or duplication-related steps

## Criterion-Specific Verification Steps

- Run `npx jscpd ./src --threshold 5` and confirm it executes and produces a duplication report
- Verify the config file sets a meaningful threshold (not disabled or set to 100%)
- Check that CI includes the duplication check step and that it can fail the build on high duplication
- For SonarQube: verify the quality gate includes a "Duplicated Lines (%)" condition
