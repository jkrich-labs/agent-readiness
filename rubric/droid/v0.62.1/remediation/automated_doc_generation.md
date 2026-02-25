---
signal_name: Automated Doc Generation
---

## Criterion-Specific Fix Guidance

- **API documentation**: If the project exposes HTTP APIs, add Swagger/OpenAPI doc generation. For Python (FastAPI), ensure `openapi_url` is not disabled and add `fastapi[all]` or use `spectree` for Flask/Django. For TypeScript/Node, add `swagger-jsdoc` + `swagger-ui-express` or `@nestjs/swagger`.
- **Python docstrings to HTML**: Configure Sphinx (`docs/conf.py`) with `autodoc` extension, or use `pdoc` / `mkdocs` with `mkdocstrings` plugin. Add a `docs` target in `pyproject.toml` scripts or a Makefile.
- **TypeScript/JavaScript**: Add `typedoc` for TypeScript projects or `jsdoc` for JavaScript. Configure via `typedoc.json` or `jsdoc.json` at the repo root.
- **Changelog generation**: Add `conventional-changelog-cli`, `git-cliff`, `towncrier` (Python), or `changesets` (JS/TS monorepos) to auto-generate changelogs from commit messages or fragment files.
- **CI integration**: Add a workflow step that generates docs on push to default branch and either commits them, publishes to GitHub Pages, or uploads as an artifact.
- **Pre-commit hook**: Consider adding a pre-commit hook that regenerates docs and fails if they are out of date, using `pre-commit` framework or `husky` + `lint-staged`.

## Criterion-Specific Exploration Steps

- Check for existing doc generation configs: `docs/conf.py` (Sphinx), `mkdocs.yml`, `typedoc.json`, `jsdoc.json`, `.storybook/`
- Look for OpenAPI/Swagger files: `openapi.yaml`, `swagger.json`, or auto-generation from framework decorators
- Check `package.json` or `pyproject.toml` for doc-related scripts (e.g., `docs`, `build:docs`, `generate-api-docs`)
- Check CI workflows (`.github/workflows/`) for doc build or publish steps
- Look for changelog tooling: `CHANGELOG.md`, `.changeset/`, `cliff.toml`, `towncrier.toml`, `changelog.d/`

## Criterion-Specific Verification Steps

- Run the doc generation command and confirm it produces output without errors (e.g., `mkdocs build`, `sphinx-build docs docs/_build`, `npx typedoc`)
- Verify that a CI workflow exists with a step that invokes doc generation
- Confirm the generated docs contain actual content (not empty stubs) reflecting the current codebase
