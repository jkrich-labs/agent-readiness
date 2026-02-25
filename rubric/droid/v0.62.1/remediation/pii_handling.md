---
signal_name: PII Handling
---

## Criterion-Specific Fix Guidance

- **Microsoft Presidio (Python)**: Install `presidio-analyzer` and `presidio-anonymizer` (`pip install presidio-analyzer presidio-anonymizer`). Scan text for PII: `from presidio_analyzer import AnalyzerEngine; analyzer = AnalyzerEngine(); results = analyzer.analyze(text="John's SSN is 123-45-6789", language="en")`. Anonymize: `from presidio_anonymizer import AnonymizerEngine; anonymizer = AnonymizerEngine(); anonymizer.anonymize(text=text, analyzer_results=results)`. Integrate into data ingestion pipelines.
- **AWS Macie**: Enable Macie on S3 buckets that store user data. Macie automatically classifies and detects PII in stored objects. Configure via Terraform: `resource "aws_macie2_account" {} resource "aws_macie2_classification_job" { ... }`. Review findings in the Macie console or export to Security Hub.
- **detect-secrets (pre-commit)**: Install `detect-secrets` (`pip install detect-secrets`). Generate a baseline: `detect-secrets scan > .secrets.baseline`. Add as a pre-commit hook: `- repo: https://github.com/Yelp/detect-secrets; hooks: [{ id: detect-secrets, args: ['--baseline', '.secrets.baseline'] }]`. While primarily for secrets, it catches PII patterns like SSNs and API keys that should not be committed.
- **Data masking in logs**: Implement log sanitization processors that redact PII fields before logging. In Python structlog: add a processor that replaces email patterns, SSNs, and credit card numbers with `[REDACTED]`. In pino (Node.js): use `redact` option: `pino({ redact: ['req.headers.authorization', '*.email', '*.ssn'] })`.
- **PII documentation**: Create a `docs/pii-handling.md` or `SECURITY.md` section that documents: what PII the application collects, where it is stored, how it is encrypted, retention policies, and how deletion requests (GDPR/CCPA) are handled. This documentation is often required for compliance audits.
- **Database-level encryption**: Ensure PII fields are encrypted at rest. Use application-level encryption for sensitive columns (`cryptography` library in Python, `crypto` module in Node.js) or enable database-level encryption (AWS RDS encryption, PostgreSQL `pgcrypto`).
- **Data classification**: Label data fields in your schema or models with sensitivity classifications. Use comments or decorators to mark PII fields: `# PII: email address` or custom validators that enforce encryption for marked fields.
- **Access controls**: Restrict access to PII data at the application level. Implement role-based access control (RBAC) so that only authorized services or users can read unmasked PII. Log all access to PII fields for audit trails.

## Criterion-Specific Exploration Steps

- Check dependencies for PII tools: `grep -E 'presidio|macie|detect-secrets|scrubadub|pii' pyproject.toml package.json`
- Search for PII-related configuration: `grep -rn 'pii\|redact\|anonymize\|mask\|sanitize\|GDPR\|CCPA' src/ docs/ .pre-commit-config.yaml`
- Look for a secrets baseline file: `.secrets.baseline`
- Check for data handling documentation: `docs/pii*.md`, `docs/data-handling.md`, `SECURITY.md`
- Search for encryption of sensitive fields: `grep -rn 'encrypt\|Fernet\|AES\|pgcrypto\|createCipheriv' src/`
- Check if the application collects PII (user registration, payment processing, etc.) to determine if this criterion applies
- Look for pre-commit hooks related to secrets/PII scanning

## Criterion-Specific Verification Steps

- Confirm at least one PII detection or handling mechanism is in place: scanning tool, documented policy, or data masking implementation
- For Presidio: run the analyzer on sample text containing PII and verify it detects entities correctly
- For detect-secrets: run `detect-secrets scan` and verify the baseline is up to date
- Check that log output does not contain unmasked PII: search log samples for email patterns, phone numbers, or SSN formats
- Verify PII handling documentation exists and covers collection, storage, and deletion procedures
- For AWS Macie: confirm classification jobs are running and findings are being reviewed
