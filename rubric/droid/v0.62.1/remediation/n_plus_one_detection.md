---
signal_name: N+1 Query Detection
---

## Criterion-Specific Fix Guidance

- **Python (Django) projects**: Install `django-query-count` or `nplusone` (`pip install nplusone`). Add `nplusone` to `INSTALLED_APPS` and `nplusone.ext.django.NPlusOneMiddleware` to `MIDDLEWARE` in your Django settings. Set `NPLUSONE_RAISE = True` in test settings to fail tests on N+1 queries. For SQLAlchemy, use `sqlalchemy.events` to detect lazy loads in tests.
- **Python (SQLAlchemy) projects**: Use `sqlalchemy-utils` or configure `echo=True` in test settings and parse logs. Consider `sqlalchemy.orm.Session.no_autoflush` and eager loading (`joinedload`, `selectinload`) to fix detected N+1s.
- **Ruby on Rails projects**: Add the `bullet` gem to the `development` and `test` groups in `Gemfile`. Configure in `config/environments/development.rb`: `Bullet.enable = true`, `Bullet.raise = true` (for tests), `Bullet.alert = true` (for browser).
- **TypeScript/JavaScript (GraphQL) projects**: Use DataLoader to batch and cache database queries. Install `dataloader` (`npm install dataloader`) and create loader instances for each entity type. This prevents N+1 queries in GraphQL resolver chains.
- **APM alternative**: If the project uses an APM tool (Datadog, New Relic, Sentry Performance), configure slow query alerting with a threshold (e.g., flag queries that repeat more than 10 times in a single request).
- This criterion is skippable: if the application does not interact with a database, it will be skipped.

## Criterion-Specific Exploration Steps

- Check for `nplusone` or `django-query-count` in Python dependencies
- Check Django `settings.py` for N+1 detection middleware
- Check `Gemfile` for `bullet` gem (Ruby)
- Check for `dataloader` in `package.json` dependencies
- Look for GraphQL schema files (`*.graphql`, `schema.graphql`) and resolver files that may need DataLoader
- Check for APM configuration (Datadog agent, New Relic config, Sentry DSN) and slow query monitoring
- Look for SQLAlchemy eager loading patterns (`joinedload`, `selectinload`, `subqueryload`) indicating awareness of N+1 issues

## Criterion-Specific Verification Steps

- **Django**: Verify `nplusone` is in `INSTALLED_APPS` and middleware is configured; run tests to confirm it activates
- **Rails**: Verify `Bullet.enable = true` is configured and run tests to confirm Bullet detects queries
- **GraphQL**: Verify DataLoader instances exist for entity types that are fetched in resolvers
- Check that N+1 detection is configured to fail in CI (not just warn in development)
