---
signal_name: Distributed Tracing
---

## Criterion-Specific Fix Guidance

- **OpenTelemetry (Python)**: Install `opentelemetry-api`, `opentelemetry-sdk`, and relevant instrumentation packages (`opentelemetry-instrumentation-fastapi`, `opentelemetry-instrumentation-requests`, `opentelemetry-instrumentation-django`). Initialize the tracer in your app startup: `from opentelemetry import trace; from opentelemetry.sdk.trace import TracerProvider; trace.set_tracer_provider(TracerProvider())`. Auto-instrument with `opentelemetry-instrument python app.py` or call `Instrumentor().instrument()` in code.
- **OpenTelemetry (TypeScript/JavaScript)**: Install `@opentelemetry/api`, `@opentelemetry/sdk-node`, `@opentelemetry/auto-instrumentations-node`. Create a `tracing.ts` file that initializes the NodeSDK with auto-instrumentations and import it first: `node --require ./tracing.js app.js` or use `--import` for ESM.
- **Request ID propagation (lightweight)**: If full OpenTelemetry is too heavy, implement request ID propagation. Generate a UUID at the API gateway or first service, pass it via `X-Request-ID` header, and include it in all log entries. In Express: `app.use((req, res, next) => { req.id = req.headers['x-request-id'] || uuidv4(); next(); })`. In Python: use middleware to extract/generate the request ID and store in context.
- **Correlation in logs**: Ensure the trace ID or request ID appears in every log line. With structlog: `logger = logger.bind(trace_id=span.get_span_context().trace_id)`. With pino: pass `traceId` in the log child context.
- **Exporter configuration**: Configure an exporter to send traces to your observability backend. Use `OTLPSpanExporter` for Jaeger, Grafana Tempo, Datadog, or any OTLP-compatible backend. For local development, use `ConsoleSpanExporter` to print traces to stdout.
- **Propagation format**: Use W3C TraceContext propagation (`traceparent` header) as the default. Configure with `set_global_textmap(TraceContextTextMapPropagator())` in Python or set `textMapPropagator` in the NodeSDK config.
- **Service name**: Always set `service.name` in the resource attributes so traces are properly attributed: `Resource(attributes={"service.name": "my-service"})`.

## Criterion-Specific Exploration Steps

- Check dependencies for tracing libraries: `grep -E 'opentelemetry|@opentelemetry|dd-trace|jaeger-client' pyproject.toml package.json`
- Search for trace initialization code: `grep -rn 'TracerProvider\|NodeSDK\|initTracing\|dd-trace' src/`
- Look for request ID middleware: `grep -rn 'X-Request-ID\|x-request-id\|requestId\|request_id\|correlation.id' src/`
- Check for trace context propagation headers: `grep -rn 'traceparent\|TraceContext\|W3CTraceContextPropagator' src/`
- Look for a tracing configuration file: `tracing.ts`, `tracing.js`, `otel.py`, `telemetry.py`
- Check environment variables in `.env` or deployment configs for `OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `DD_TRACE_ENABLED`

## Criterion-Specific Verification Steps

- Confirm a tracing SDK is initialized in the application startup path (not just installed as a dependency)
- Run the application locally with `ConsoleSpanExporter` or `OTEL_TRACES_EXPORTER=console` and make a request; verify trace output appears in stdout
- Confirm trace IDs or request IDs appear in structured log entries
- Check that downstream HTTP calls include propagation headers (inspect with `curl -v` or browser dev tools)
- Verify the service name is set correctly in trace resource attributes
