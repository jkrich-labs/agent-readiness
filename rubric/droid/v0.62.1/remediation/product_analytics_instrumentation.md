---
signal_name: Product Analytics Instrumentation
---

## Criterion-Specific Fix Guidance

- **PostHog (open-source, self-hostable)**: Install `posthog-js` (frontend) or `posthog-node` (backend). Initialize: `posthog.init('phc_...', { api_host: 'https://app.posthog.com' })`. Track events: `posthog.capture('user_signed_up', { plan: 'pro', source: 'landing_page' })`. Identify users: `posthog.identify(userId, { email, name })`. PostHog also supports feature flags, session replay, and A/B testing.
- **Mixpanel (TypeScript/JavaScript)**: Install `mixpanel-browser` (frontend) or `mixpanel` (backend). Initialize: `mixpanel.init('TOKEN')`. Track events: `mixpanel.track('Purchase', { item: 'Premium Plan', price: 29.99 })`. Identify users: `mixpanel.identify(userId); mixpanel.people.set({ '$email': email })`.
- **Amplitude**: Install `@amplitude/analytics-browser` (frontend) or `@amplitude/analytics-node` (backend). Initialize: `amplitude.init('API_KEY')`. Track: `amplitude.track('Button Clicked', { buttonName: 'checkout' })`. Identify: `amplitude.setUserId(userId)`.
- **Google Analytics 4 (GA4)**: Add the GA4 script tag or install `@analytics/google-analytics`. Track custom events: `gtag('event', 'purchase', { value: 29.99, currency: 'USD' })`. For single-page apps, ensure page view tracking fires on route changes.
- **Python backend tracking**: For server-side analytics, use the respective SDK's server library. PostHog: `from posthog import Posthog; posthog = Posthog('phc_...', host='https://app.posthog.com'); posthog.capture(distinct_id=user_id, event='subscription_created', properties={'plan': 'pro'})`. Mixpanel: `from mixpanel import Mixpanel; mp = Mixpanel('TOKEN'); mp.track(user_id, 'Subscription Created', {'plan': 'pro'})`.
- **Event naming conventions**: Adopt a consistent naming convention for events. Use `Object Action` format (e.g., `User Signed Up`, `Payment Completed`, `Feature Enabled`) or `snake_case` (`user_signed_up`). Document the convention in a `docs/analytics-events.md` or tracking plan.
- **Tracking plan**: Create a tracking plan document that lists all tracked events, their properties, and when they fire. This prevents ad-hoc event proliferation and ensures analytics data is meaningful. Tools like Avo or Segment Protocols can enforce the tracking plan.
- **Privacy compliance**: Ensure analytics respects user consent preferences. Implement a consent banner and only initialize analytics after consent is granted. Use PostHog's `opt_out_capturing()` or Mixpanel's `opt_out_tracking()` for users who decline.

## Criterion-Specific Exploration Steps

- Check dependencies for analytics SDKs: `grep -E 'posthog|mixpanel|amplitude|@analytics|heap|segment' package.json pyproject.toml`
- Search for analytics initialization: `grep -rn 'posthog.init\|mixpanel.init\|amplitude.init\|gtag\|analytics.page\|Posthog(' src/`
- Look for event tracking calls: `grep -rn '\.track(\|\.capture(\|gtag.*event\|analytics.track' src/`
- Check for GA4 script tags in HTML templates: `grep -rn 'googletagmanager\|gtag.js\|GA_MEASUREMENT_ID' src/ public/ templates/`
- Look for a tracking plan or analytics documentation: `docs/analytics*`, `docs/tracking*`, `ANALYTICS.md`
- Check for consent management: `grep -rn 'consent\|opt_out\|cookie.*banner\|gdpr' src/`
- Determine if the app has a user-facing frontend (backend-only APIs may track events server-side or may not need product analytics)

## Criterion-Specific Verification Steps

- Confirm an analytics SDK is installed and initialized in the application code
- Verify at least one custom event is being tracked (not just default page views)
- For frontend analytics, open browser dev tools Network tab, perform an action, and verify analytics requests are sent to the provider endpoint
- For server-side analytics, check application logs or the analytics provider dashboard for events
- Verify user identification is implemented (events are associated with user IDs, not just anonymous sessions)
- Check that analytics respects consent/opt-out mechanisms if required by the application's privacy policy
