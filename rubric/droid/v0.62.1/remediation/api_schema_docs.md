---
signal_name: API Schema Documentation
---

## Criterion-Specific Fix Guidance

- **OpenAPI/Swagger for REST APIs**: Create an `openapi.yaml` or `openapi.json` file at the project root or in a `docs/` directory. Use OpenAPI 3.0+ format. At minimum, define `info`, `paths`, and `components/schemas` sections. Tools like `swagger-jsdoc` (Node.js) or `drf-spectacular` (Django) can auto-generate from code annotations.
- **Python (FastAPI)**: FastAPI generates OpenAPI schemas automatically at `/docs` and `/openapi.json`. Ensure endpoint functions have type hints and Pydantic models for request/response bodies. Export the schema with `python -c "from app.main import app; import json; print(json.dumps(app.openapi()))" > openapi.json`.
- **Python (Django REST Framework)**: Install `drf-spectacular` (`pip install drf-spectacular`), add to `INSTALLED_APPS`, and configure `DEFAULT_SCHEMA_CLASS` to `drf_spectacular.openapi.AutoSchema`. Generate with `python manage.py spectacular --file openapi.yaml`.
- **TypeScript/JavaScript (Express/NestJS)**: For Express, use `swagger-jsdoc` with JSDoc annotations on route handlers, combined with `swagger-ui-express`. For NestJS, use `@nestjs/swagger` module and decorate controllers with `@ApiTags`, `@ApiResponse`, etc.
- **GraphQL schemas**: Ensure a `schema.graphql` or `schema.gql` file exists, or that the schema is exportable via introspection. Use `graphql-codegen` to generate typed client code. For Apollo Server, the schema is typically defined inline but should be exported as a `.graphql` file for documentation.
- **Schema validation in CI**: Add a CI step to validate the schema: `npx @redocly/cli lint openapi.yaml` or `python -m openapi_spec_validator openapi.yaml`.
- **Keep schema in sync**: Use `openapi-diff` or `oasdiff` in CI to detect breaking changes between the PR branch and main branch schemas.

## Criterion-Specific Exploration Steps

- Search for existing schema files: `openapi.yaml`, `openapi.json`, `swagger.yaml`, `swagger.json`, `schema.graphql`, `schema.gql`
- Check if FastAPI is used (auto-generates OpenAPI): look for `from fastapi import FastAPI` in source
- Check for DRF + drf-spectacular: look for `drf_spectacular` in `INSTALLED_APPS` or `pyproject.toml`
- Check for `@nestjs/swagger` or `swagger-jsdoc` in `package.json`
- Look for GraphQL schema definitions: `grep -rn 'type Query' --include='*.graphql' --include='*.gql' --include='*.ts' --include='*.py'`
- Check if the project has API routes at all (some apps are purely frontend and this criterion may not apply)

## Criterion-Specific Verification Steps

- Confirm a schema file exists and is valid: `npx @redocly/cli lint openapi.yaml` or `python -m openapi_spec_validator openapi.json`
- For FastAPI, start the dev server and confirm `/docs` renders the Swagger UI
- For GraphQL, run an introspection query and confirm the schema is non-empty
- Verify the schema covers at least the main API endpoints (not just a skeleton with one path)
- Check that request/response models have defined properties, not just empty objects
