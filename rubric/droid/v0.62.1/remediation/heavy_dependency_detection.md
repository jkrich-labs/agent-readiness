---
signal_name: Heavy Dependency Detection
---

## Criterion-Specific Fix Guidance

- **TypeScript/JavaScript projects**: Install `webpack-bundle-analyzer` (`npm install -D webpack-bundle-analyzer`) and add it as a plugin in your Webpack config. Run `npx webpack-bundle-analyzer stats.json` to visualize bundle composition. For non-Webpack projects (Vite, Rollup), use `rollup-plugin-visualizer`.
- **size-limit (preferred for CI)**: Install `size-limit` and `@size-limit/preset-app` or `@size-limit/preset-small-lib` (`npm install -D size-limit @size-limit/preset-app`). Add config to `package.json`: `"size-limit": [{ "path": "dist/**/*.js", "limit": "250 KB" }]` and a script: `"size": "size-limit"`. This fails CI when bundle size exceeds the limit.
- **Lighthouse CI**: Install `@lhci/cli` (`npm install -D @lhci/cli`) and create `lighthouserc.js` with performance budgets. Run `lhci autorun` in CI to check total bundle weight and loading performance.
- **Import cost awareness**: Install the `import-cost` VS Code extension for real-time feedback on import sizes. Use `bundlephobia.com` to evaluate package sizes before adding dependencies.
- **Python projects**: While bundle size is less of a concern for backend Python, use `pipdeptree` to visualize dependency trees and identify heavy transitive dependencies. Consider `pip install` size tracking in Docker builds.
- This criterion is skippable: if the application is a backend-only service with no client-side bundle, it may not be applicable.
- Add bundle size checking to CI as a required step to prevent size regressions.

## Criterion-Specific Exploration Steps

- Check `package.json` for `webpack-bundle-analyzer`, `size-limit`, `@lhci/cli`, or `rollup-plugin-visualizer` in `devDependencies`
- Check for `size-limit` config in `package.json` or `.size-limit.json`
- Check for `lighthouserc.js` or `.lighthouserc.json` at the repo root
- Check Webpack config for `BundleAnalyzerPlugin`
- Check CI workflows for bundle size or Lighthouse steps
- Look for performance budgets in Lighthouse CI or custom scripts

## Criterion-Specific Verification Steps

- Run `npx size-limit` and confirm it executes and reports bundle sizes against configured limits
- Verify the size limit threshold is set to a reasonable value (not an extremely high placeholder)
- Check that CI includes the bundle size check and can fail the build on size regressions
- For Lighthouse CI: run `lhci autorun --collect.staticDistDir=dist` and confirm performance budgets are evaluated
