---
signal_name: Error Tracking Contextualized
---

## Criterion-Specific Fix Guidance

- **Sentry (Python)**: Install `sentry-sdk` (`pip install sentry-sdk`). Initialize early in app startup: `import sentry_sdk; sentry_sdk.init(dsn="...", traces_sample_rate=0.1, environment="production")`. For Django, the SDK auto-instruments. For FastAPI, add `sentry_sdk.init(dsn="...", integrations=[StarletteIntegration(), FastApiIntegration()])`. Set user context: `sentry_sdk.set_user({"id": user.id, "email": user.email})`.
- **Sentry (TypeScript/JavaScript)**: Install `@sentry/node` and `@sentry/browser` (for frontend). Initialize with `Sentry.init({ dsn: "...", integrations: [new Sentry.Integrations.Http({ tracing: true })], tracesSampleRate: 0.1 })`. Add breadcrumbs: `Sentry.addBreadcrumb({ message: "User clicked checkout", category: "ui.click" })`.
- **Source maps**: For frontend JavaScript/TypeScript, upload source maps to Sentry during the build step. Use `@sentry/webpack-plugin`, `@sentry/vite-plugin`, or the Sentry CLI: `sentry-cli sourcemaps upload --release=VERSION ./dist`. This enables readable stack traces instead of minified code references.
- **Breadcrumbs**: Configure automatic breadcrumb capture for HTTP requests, console messages, and DOM interactions. Add custom breadcrumbs at key application decision points (e.g., before database queries, after authentication). This provides context for what happened before an error.
- **User context**: Always set user identity on the Sentry scope so errors can be correlated to specific users. Call `sentry_sdk.set_user()` or `Sentry.setUser()` after authentication. Include at minimum a user ID; optionally include email and username.
- **Bugsnag alternative**: Install `bugsnag` (`pip install bugsnag` / `npm install @bugsnag/js`). Initialize with `bugsnag.start({ apiKey: "..." })`. Add metadata: `bugsnag.notify(err, event => { event.addMetadata("user", { id: userId }) })`.
- **Rollbar alternative**: Install `rollbar` (`pip install rollbar` / `npm install rollbar`). Initialize with `Rollbar({ accessToken: "...", environment: "production" })`. Configure person tracking for user context.
- **Environment separation**: Always configure the `environment` parameter (production, staging, development) so errors are properly segmented and production issues are prioritized.

## Criterion-Specific Exploration Steps

- Check dependencies for error tracking SDKs: `grep -E 'sentry-sdk|@sentry|bugsnag|rollbar' pyproject.toml package.json`
- Search for SDK initialization: `grep -rn 'sentry_sdk.init\|Sentry.init\|bugsnag.start\|Rollbar(' src/`
- Check for source map upload configuration: `grep -rn 'sourcemaps\|SentryWebpackPlugin\|sentryVitePlugin\|sentry-cli' webpack.config.* vite.config.* .github/workflows/*`
- Look for user context setting: `grep -rn 'set_user\|setUser\|addMetadata\|person' src/`
- Check for breadcrumb configuration: `grep -rn 'addBreadcrumb\|breadcrumb' src/`
- Verify DSN/API key is provided via environment variable, not hardcoded: `grep -rn 'dsn.*=.*https://' src/`

## Criterion-Specific Verification Steps

- Confirm the error tracking SDK is initialized in the application entry point (not just installed)
- Trigger a test error and verify it appears in the Sentry/Bugsnag/Rollbar dashboard with full stack trace
- For frontend apps, verify source maps are uploaded: stack traces should show original source file names and line numbers, not minified bundles
- Confirm user context is attached: trigger an error after authentication and check that user info appears in the error event
- Verify breadcrumbs are present: check that the error event shows recent actions leading up to the error
- Confirm `environment` is set correctly (not blank or defaulting to "development" in production)
