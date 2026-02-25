---
signal_name: Health Checks
---

## Criterion-Specific Fix Guidance

- **HTTP health endpoint (Python/FastAPI)**: Add a `/health` or `/healthz` route that returns 200 with a JSON body: `@app.get("/health") def health(): return {"status": "ok"}`. For deeper checks, verify database connectivity and external service availability, returning 503 if any dependency is unhealthy.
- **HTTP health endpoint (Express/Node.js)**: Add `app.get('/health', (req, res) => res.json({ status: 'ok' }))`. For a more comprehensive check, ping the database and return `{ status: 'ok', db: 'connected' }` or `{ status: 'degraded', db: 'unreachable' }` with appropriate HTTP status codes.
- **Django health check**: Install `django-health-check` (`pip install django-health-check`), add to `INSTALLED_APPS`, and configure URL: `path('health/', include('health_check.urls'))`. Add backends for database, cache, and storage checks.
- **NestJS health check**: Install `@nestjs/terminus` (`npm install @nestjs/terminus`). Create a health controller using `HealthCheckService` with indicators for database (`TypeOrmHealthIndicator`), HTTP dependencies (`HttpHealthIndicator`), and memory (`MemoryHealthIndicator`).
- **Kubernetes probes**: Add liveness and readiness probes to your Kubernetes deployment manifest. Liveness probe: `livenessProbe: { httpGet: { path: /health, port: 8080 }, initialDelaySeconds: 15, periodSeconds: 10 }`. Readiness probe should check dependency availability (database, cache) while liveness should only check if the process is responsive.
- **Docker HEALTHCHECK**: Add to Dockerfile: `HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8080/health || exit 1`. This enables Docker and Docker Compose to detect unhealthy containers and restart them.
- **Separate liveness vs. readiness**: Implement two endpoints: `/healthz` (liveness -- is the process alive?) and `/readyz` (readiness -- can it accept traffic?). Liveness should be trivial (return 200). Readiness should verify database connections, cache availability, and other critical dependencies.
- **Startup probe**: For applications with slow startup (loading ML models, warming caches), add a Kubernetes startup probe with a longer timeout to prevent premature restarts: `startupProbe: { httpGet: { path: /health, port: 8080 }, failureThreshold: 30, periodSeconds: 10 }`.

## Criterion-Specific Exploration Steps

- Search for existing health endpoints: `grep -rn '/health\|/healthz\|/readyz\|/ready\|/live\|/liveness' src/ app/`
- Check Kubernetes manifests for probe definitions: `grep -rn 'livenessProbe\|readinessProbe\|startupProbe' k8s/ deploy/ helm/ manifests/`
- Check Dockerfiles for HEALTHCHECK: `grep -rn 'HEALTHCHECK' Dockerfile*`
- Look for health check libraries: `grep -E 'django-health-check|@nestjs/terminus|@godaddy/terminus' pyproject.toml package.json`
- Check Docker Compose for healthcheck configuration: `grep -A5 'healthcheck' docker-compose*.yml`
- Determine if the app is an HTTP service (if it is a CLI tool or batch job, health checks may not apply)

## Criterion-Specific Verification Steps

- Start the application and send a request to the health endpoint: `curl -v http://localhost:8080/health` -- confirm it returns 200 with a JSON body
- If readiness checks are implemented, stop the database and verify the readiness endpoint returns 503
- For Kubernetes, verify probe definitions are present in deployment manifests and match actual endpoint paths
- For Docker, run `docker inspect <container>` and verify the health status shows "healthy"
- Confirm the health endpoint does not require authentication (load balancers and orchestrators need unauthenticated access)
- Verify the health check responds quickly (under 1 second) -- slow health checks can cause cascading restarts
