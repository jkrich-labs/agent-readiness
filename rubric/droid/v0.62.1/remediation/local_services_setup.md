---
signal_name: Local Services Setup
---

## Criterion-Specific Fix Guidance

- Create a `docker-compose.yml` (or `compose.yml` for Docker Compose v2) at the repository root that defines all local service dependencies (databases, caches, message queues, etc.).
- **Common services to include**:
  - PostgreSQL: `postgres:16-alpine` with `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` environment variables
  - Redis: `redis:7-alpine` with appropriate port mapping
  - Elasticsearch, RabbitMQ, Kafka, etc. as needed by the application
- Map ports to localhost so the application can connect without Docker networking: `ports: ["5432:5432"]`.
- Add health checks so dependent services wait for readiness:
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    timeout: 5s
    retries: 5
  ```
- Use `volumes` for data persistence during development (named volumes, not bind mounts for databases).
- Add a `Makefile` target or `package.json` script for convenience: `make services-up` or `npm run services:start` that wraps `docker compose up -d`.
- **Alternative**: If Docker is not feasible, document local service setup clearly in `README.md` or `CONTRIBUTING.md` with exact install commands for each dependency (e.g., `brew install postgresql@16`).
- Include seed/migration commands that run after services start (e.g., `docker compose exec db psql -f seed.sql`).

## Criterion-Specific Exploration Steps

- Check if `docker-compose.yml`, `compose.yml`, or `docker-compose.override.yml` already exists
- Look at application config files to identify required services: database URLs, cache connections, queue connections
- Check `README.md` or `CONTRIBUTING.md` for existing local setup instructions
- Search source code for connection strings: `DATABASE_URL`, `REDIS_URL`, `AMQP_URL`, `ELASTICSEARCH_URL`
- Check if the project uses `testcontainers` or similar for test-time services

## Criterion-Specific Verification Steps

- Confirm `docker-compose.yml` exists and is valid YAML (`docker compose config` exits cleanly)
- Run `docker compose up -d` and verify all services reach healthy/running state
- Confirm the application can connect to the local services after they start
- If no Docker Compose file exists, verify that `README.md` contains clear local service setup instructions
