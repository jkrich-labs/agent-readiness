---
signal_name: Structured Logging
---

## Criterion-Specific Fix Guidance

- **Python (structlog)**: Install `structlog` (`pip install structlog`). Configure in an early startup module: `structlog.configure(processors=[structlog.processors.TimeStamper(fmt="iso"), structlog.processors.JSONRenderer()])`. Replace all `print()` debugging with `logger = structlog.get_logger(); logger.info("event_name", key="value")`. Bind contextual data with `logger = logger.bind(request_id=req_id)`.
- **Python (loguru)**: Install `loguru` (`pip install loguru`). Use `from loguru import logger` directly. Configure JSON output with `logger.add(sys.stdout, serialize=True)`. Add structured context with `logger.bind(user_id=uid).info("action performed")`.
- **Python (stdlib logging + JSON)**: If adding a dependency is not desired, use `python-json-logger`: `pip install python-json-logger`, then configure a `JsonFormatter` on the root logger handler. All log records will emit JSON.
- **TypeScript/JavaScript (pino)**: Install `pino` (`npm install pino`). Create a logger instance: `import pino from 'pino'; const logger = pino({ level: 'info' });`. Use `logger.info({ requestId, userId }, 'request handled')` for structured fields. Pino emits JSON by default and is the fastest Node.js logger.
- **TypeScript/JavaScript (winston)**: Install `winston` (`npm install winston`). Configure with JSON format: `const logger = winston.createLogger({ format: winston.format.json(), transports: [new winston.transports.Console()] })`. Add metadata with `logger.info('message', { key: 'value' })`.
- **Replace console.log/print**: Search for `console.log`, `console.error`, `print(` calls in application code and replace with structured logger calls. Retain `console.*` only in CLI tools or build scripts where structured logging is unnecessary.
- **Create a shared logger module**: Define a `src/lib/logger.ts` or `src/logging_config.py` that configures the logger once. Import from this module throughout the codebase to ensure consistent configuration.
- **Log levels**: Use appropriate levels: `debug` for development detail, `info` for normal operations, `warn` for recoverable issues, `error` for failures. Never log sensitive data (passwords, tokens, PII) at any level.

## Criterion-Specific Exploration Steps

- Check dependencies for logging libraries: `grep -E 'structlog|loguru|python-json-logger' pyproject.toml` or `grep -E 'pino|winston|bunyan' package.json`
- Search for existing logger configuration: `grep -rn 'structlog.configure\|getLogger\|createLogger\|pino(' src/ lib/ app/`
- Check for unstructured logging: `grep -rn 'console.log\|console.error\|print(' src/ --include='*.ts' --include='*.py' --include='*.js'`
- Look for a dedicated logger module: `logger.ts`, `logger.js`, `logger.py`, `logging_config.py`
- Check if any logging middleware is configured (e.g., Express request logging with `pino-http` or `morgan`)

## Criterion-Specific Verification Steps

- Confirm a structured logging library is in project dependencies (not just installed globally)
- Run the application or tests and verify log output is JSON (pipe through `jq .` to validate)
- Check that at least the main entry point or request handler uses the structured logger
- Verify log entries include a timestamp, log level, and message field at minimum
- Confirm no sensitive data appears in log output by reviewing log samples
