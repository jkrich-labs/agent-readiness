---
signal_name: Integration Tests Exist
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript (E2E) projects**: Install Playwright (`npm install -D @playwright/test`) and create `playwright.config.ts` at the repo root. Create test files in an `e2e/` or `tests/` directory using `*.spec.ts` naming. Alternatively, install Cypress (`npm install -D cypress`) which creates a `cypress/` directory structure with `cypress/e2e/` for test files.
- **Python projects**: Create an `tests/integration/` directory and place integration test files there using `test_*.py` naming. Use pytest with markers: decorate integration tests with `@pytest.mark.integration` and configure `pyproject.toml` with `markers = ["integration: integration tests"]`. This allows running them separately: `pytest -m integration`.
- **Python (BDD) projects**: Install Behave (`pip install behave`) and create `.feature` files in a `features/` directory using Gherkin syntax. Create step definitions in `features/steps/`.
- **Playwright setup**: Run `npx playwright install` to install browsers. Create a minimal test: `test('example', async ({ page }) => { await page.goto('/'); await expect(page).toHaveTitle(/App/); });`.
- **Cypress setup**: Run `npx cypress open` to scaffold the directory structure. Create a test in `cypress/e2e/` that visits a page and makes assertions.
- Separate integration tests from unit tests so they can be run independently in CI (typically in a later pipeline stage after unit tests pass).
- Add integration test execution to CI workflows, typically after the build step and before deployment.

## Criterion-Specific Exploration Steps

- Check for `cypress/` directory and `cypress.config.ts` or `cypress.config.js`
- Check for `playwright.config.ts` or `playwright.config.js` at the repo root
- Check for `tests/integration/` directory or `e2e/` directory
- Search for `.feature` files (Gherkin/BDD tests) in `features/` directory
- Check `package.json` for `cypress`, `@playwright/test`, or `puppeteer` in `devDependencies`
- Check Python dependencies for `behave`, `selenium`, `playwright`
- Check CI workflows for integration or E2E test steps (often a separate job)
- Look for pytest markers like `@pytest.mark.integration` in test files

## Criterion-Specific Verification Steps

- Confirm integration/E2E test files exist in the expected locations (`cypress/e2e/`, `e2e/`, `tests/integration/`, `features/`)
- Verify test files contain actual test cases (not just scaffolded examples)
- Run `npx playwright test --list` or `npx cypress run --spec 'cypress/e2e/**'` to confirm tests are discoverable
- For Python: run `pytest tests/integration/ --collect-only` or `pytest -m integration --collect-only` to confirm discovery
