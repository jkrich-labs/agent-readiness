---
signal_name: Log Scrubbing
---

## Criterion-Specific Fix Guidance

- **Pino redact (TypeScript/JavaScript)**: Configure pino with the `redact` option to automatically remove sensitive fields from log output: `const logger = pino({ redact: { paths: ['req.headers.authorization', 'req.headers.cookie', '*.password', '*.token', '*.ssn', '*.creditCard', '*.email'], censor: '[REDACTED]' } })`. This applies to all log calls using this logger instance without requiring per-call changes.
- **Winston format (TypeScript/JavaScript)**: Create a custom Winston format that sanitizes sensitive data: `const scrubFormat = winston.format((info) => { if (info.password) info.password = '[REDACTED]'; return info; })()`. Apply it in the format chain: `format: winston.format.combine(scrubFormat, winston.format.json())`. For regex-based scrubbing, use a format that replaces patterns matching emails, credit cards, and SSNs.
- **structlog processors (Python)**: Add a custom processor that scrubs sensitive fields: `def scrub_sensitive(_, __, event_dict): for key in ['password', 'token', 'authorization', 'ssn', 'credit_card']: if key in event_dict: event_dict[key] = '[REDACTED]'; return event_dict`. Register it: `structlog.configure(processors=[scrub_sensitive, ..., structlog.processors.JSONRenderer()])`.
- **loguru patching (Python)**: Use loguru's `patch` feature to intercept and sanitize records: `logger = logger.patch(lambda record: record.update({"extra": {k: "[REDACTED]" if k in SENSITIVE_KEYS else v for k, v in record["extra"].items()}}))`.
- **Regex-based scrubbing**: For defense-in-depth, add a regex processor that catches PII patterns regardless of field names. Patterns to redact: email (`\b[\w.+-]+@[\w-]+\.[\w.]+\b`), SSN (`\b\d{3}-\d{2}-\d{4}\b`), credit card (`\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b`), JWT tokens (`\beyJ[\w-]+\.[\w-]+\.[\w-]+\b`).
- **Middleware-level scrubbing**: Add request logging middleware that automatically scrubs sensitive headers before logging. Strip `Authorization`, `Cookie`, `X-Api-Key`, and `Set-Cookie` headers from request/response logs. In Express: `req.headers = { ...req.headers, authorization: '[REDACTED]' }` before logging.
- **Testing log scrubbing**: Write tests that verify sensitive data does not appear in log output. Capture log output in a string buffer, log a record with known PII values, and assert the output does not contain the original values.
- **Centralized logger module**: Implement scrubbing in a single shared logger module (`src/lib/logger.ts` or `src/logging_config.py`) so all application code inherits the sanitization without per-module configuration.

## Criterion-Specific Exploration Steps

- Check for pino redact configuration: `grep -rn 'redact' src/ --include='*.ts' --include='*.js'`
- Check for Winston custom formats: `grep -rn 'winston.format\|createLogger' src/ --include='*.ts' --include='*.js'`
- Check for structlog processors: `grep -rn 'structlog.configure\|processors.*=' src/ --include='*.py'`
- Search for sanitization patterns: `grep -rn 'REDACTED\|sanitize\|scrub\|redact\|mask' src/`
- Look for a centralized logger module: `logger.ts`, `logger.js`, `logger.py`, `logging.py`, `logging_config.py`
- Check if sensitive headers are being logged: `grep -rn 'req.headers\|request.headers\|authorization' src/` to identify where scrubbing is needed
- Look for tests that verify log scrubbing: `grep -rn 'REDACTED\|scrub\|sanitize' tests/`

## Criterion-Specific Verification Steps

- Confirm a log scrubbing mechanism is configured in the logger (redact paths, custom processors, or format functions)
- Test by logging a record with sensitive data (`password`, `authorization` header, email address) and verifying the output contains `[REDACTED]` instead of the actual value
- Verify regex-based scrubbing catches PII patterns: log a string containing an email address or SSN and confirm it is masked
- Check that `Authorization` and `Cookie` headers are never present in request log output
- Run the application, make authenticated requests, and inspect log output for leaked credentials or tokens
- Verify the scrubbing is applied globally via a centralized logger, not just in isolated locations
