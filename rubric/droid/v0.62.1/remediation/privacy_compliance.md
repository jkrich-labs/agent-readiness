---
signal_name: Privacy Compliance
---

## Criterion-Specific Fix Guidance

- Implement at least one of: consent management SDK, data retention policies, or GDPR/CCPA request handling.
- **Consent management**:
  - For web frontends, integrate a consent management platform (CMP) SDK such as OneTrust, Cookiebot, or the open-source `osano/cookieconsent`. The SDK should gate analytics, marketing, and tracking scripts behind user consent.
  - Add a cookie banner component that loads before any third-party scripts and records consent preferences.
  - For APIs, implement consent flags on user records and check them before processing personal data.
- **Data retention policies**:
  - Document retention periods for each category of personal data in a `docs/data-retention.md` or `PRIVACY.md` file.
  - Implement automated data cleanup: scheduled jobs (cron, Celery beat, cloud schedulers) that purge or anonymize records past their retention period.
  - For databases, add `created_at` and `expires_at` columns to tables containing personal data.
- **GDPR/CCPA request handling**:
  - Implement data export (Subject Access Request / "Right to Access"): an endpoint or script that exports all personal data for a given user in a structured format (JSON, CSV).
  - Implement data deletion (Right to Erasure / "Right to be Forgotten"): an endpoint or script that deletes or anonymizes all personal data for a given user across all datastores.
  - Document the process in a `docs/privacy-requests.md` runbook.
- **Code-level patterns**: Search for PII fields (email, name, phone, IP address, location) and ensure they are handled appropriately — encrypted at rest, excluded from logs, and covered by retention policies.

## Criterion-Specific Exploration Steps

- Search for existing privacy/consent code: `cookie`, `consent`, `gdpr`, `ccpa`, `privacy`, `data_retention`, `anonymize`, `purge`
- Check for privacy policy documents: `PRIVACY.md`, `docs/privacy*`, `docs/data-retention*`
- Look for consent management SDKs in `package.json` (e.g., `cookieconsent`, `@onetrust/*`, `@cookiebot/*`)
- Check for data deletion or export endpoints in API routes
- Look for scheduled cleanup jobs or data retention cron tasks
- Check database migrations for `expires_at` or soft-delete patterns

## Criterion-Specific Verification Steps

- Confirm at least one privacy compliance mechanism exists: consent SDK integration, data retention documentation/automation, or data request handling code
- If a consent SDK is present, verify it loads on the frontend and gates third-party scripts
- If data retention is documented, verify the retention periods are specific (not vague) and automation exists to enforce them
- If data export/deletion endpoints exist, verify they cover all known PII storage locations
