---
signal_name: Circuit Breakers
---

## Criterion-Specific Fix Guidance

- **Python (tenacity for retries + circuit breaking)**: Install `tenacity` (`pip install tenacity`). Wrap external service calls with retry and circuit breaker logic: `from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type; @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10), retry=retry_if_exception_type(ConnectionError)) def call_external_service(): ...`. For a full circuit breaker, use `pybreaker`: `pip install pybreaker; breaker = CircuitBreaker(fail_max=5, reset_timeout=60); @breaker def call_service(): ...`.
- **Python (pybreaker)**: Install `pybreaker` (`pip install pybreaker`). Create a breaker per external dependency: `import pybreaker; db_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)`. Decorate external calls: `@db_breaker def query_database(): ...`. Handle `pybreaker.CircuitBreakerError` to return graceful fallbacks.
- **TypeScript/JavaScript (opossum)**: Install `opossum` (`npm install opossum`). Wrap external calls: `import CircuitBreaker from 'opossum'; const breaker = new CircuitBreaker(callExternalService, { timeout: 3000, errorThresholdPercentage: 50, resetTimeout: 30000 }); breaker.fallback(() => cachedResult);`. Listen to events: `breaker.on('open', () => logger.warn('Circuit opened'))`.
- **Service mesh (Istio/Linkerd)**: If using a service mesh, configure circuit breaking at the infrastructure level. In Istio: `DestinationRule` with `outlierDetection: { consecutive5xxErrors: 5, interval: 30s, baseEjectionTime: 30s }`. This requires no code changes but needs Kubernetes and a service mesh deployment.
- **Resilience4j (Java/Kotlin)**: If the application uses JVM languages, add `resilience4j-circuitbreaker` to dependencies. Configure via `application.yml`: `resilience4j.circuitbreaker.instances.externalService.failureRateThreshold: 50`.
- **Fallback strategies**: Every circuit breaker should have a fallback: return cached data, a default response, or a graceful degradation message. Never let an open circuit result in an unhandled exception to the end user.
- **Monitoring**: Log circuit state transitions (closed -> open -> half-open -> closed) and expose circuit breaker state as a metric. This enables alerting when a circuit opens, indicating a downstream dependency issue.
- **Timeout configuration**: Always set timeouts on external HTTP calls independent of the circuit breaker. Use `httpx` with `timeout=5.0` (Python) or `axios` with `timeout: 5000` (TypeScript). The circuit breaker wraps around the timeout to track failures.

## Criterion-Specific Exploration Steps

- Check dependencies for circuit breaker libraries: `grep -E 'opossum|pybreaker|tenacity|resilience4j|polly|cockatiel' package.json pyproject.toml`
- Search for circuit breaker initialization: `grep -rn 'CircuitBreaker\|circuit.breaker\|opossum\|pybreaker' src/`
- Check for retry logic: `grep -rn '@retry\|retryWhen\|retry(\|withRetry' src/`
- Look for service mesh circuit breaker config: `grep -rn 'outlierDetection\|circuitBreaker' k8s/ istio/ helm/`
- Check for timeout configuration on HTTP clients: `grep -rn 'timeout.*=\|timeout:' src/ --include='*.ts' --include='*.py' --include='*.js'`
- Determine which external services the app calls (databases, third-party APIs, microservices) to identify where circuit breakers are needed

## Criterion-Specific Verification Steps

- Confirm a circuit breaker library is installed and used to wrap at least one external service call
- Test the circuit breaker by simulating failures: stop the external service and verify the circuit opens after the configured failure threshold
- Verify a fallback is defined and returns a meaningful response when the circuit is open
- Check that circuit state changes are logged (look for "circuit open" or similar messages in logs)
- For service mesh implementations, verify the `DestinationRule` or equivalent configuration is applied: `kubectl get destinationrule -o yaml`
- Confirm timeouts are configured on the underlying HTTP client, not just relying on the circuit breaker timeout
