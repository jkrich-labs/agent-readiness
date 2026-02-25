---
signal_name: Database Schema
---

## Criterion-Specific Fix Guidance

- **Prisma (TypeScript/JavaScript)**: Create a `prisma/schema.prisma` file defining your data models. Run `npx prisma init` to scaffold. Define models with fields, relations, and indexes. Generate migrations with `npx prisma migrate dev --name init`. Ensure `prisma/migrations/` is committed to version control.
- **TypeORM (TypeScript)**: Define entities in `src/entities/` using TypeORM decorators (`@Entity`, `@Column`, `@PrimaryGeneratedColumn`). Create a `data-source.ts` or `ormconfig.json` configuration. Generate migrations with `npx typeorm migration:generate -d data-source.ts src/migrations/InitialMigration`.
- **Drizzle (TypeScript)**: Define schemas in `src/db/schema.ts` using Drizzle's table builders. Configure `drizzle.config.ts` and generate migrations with `npx drizzle-kit generate:pg` (or mysql/sqlite variant).
- **SQLAlchemy (Python)**: Define models inheriting from `Base = declarative_base()` in a `models.py` or `models/` package. Use Alembic for migrations: `alembic init alembic`, configure `alembic/env.py` with your `Base.metadata`, then `alembic revision --autogenerate -m "initial"`.
- **Django (Python)**: Define models in `<app>/models.py` using `django.db.models`. Run `python manage.py makemigrations` and `python manage.py migrate`. Ensure `migrations/` directories are committed.
- **Raw SQL migrations**: If not using an ORM, create a `migrations/` or `db/migrations/` directory with numbered SQL files (e.g., `001_create_users.sql`, `002_add_posts.sql`). Use a migration runner like `golang-migrate`, `flyway`, or `dbmate`.
- **Schema documentation**: Whether using an ORM or raw SQL, ensure the schema is visible in the repository. Avoid relying solely on a remote database as the schema source of truth.

## Criterion-Specific Exploration Steps

- Search for ORM schema files: `prisma/schema.prisma`, `**/models.py`, `**/entities/*.ts`, `**/schema.ts`
- Check for migration directories: `prisma/migrations/`, `alembic/versions/`, `migrations/`, `db/migrations/`
- Look for ORM dependencies in `package.json` (`prisma`, `typeorm`, `drizzle-orm`, `sequelize`, `knex`) or `pyproject.toml` (`sqlalchemy`, `alembic`, `django`)
- Check for raw SQL files: `*.sql` in `db/`, `sql/`, `migrations/` directories
- Look for database connection configuration: `.env` files with `DATABASE_URL`, `data-source.ts`, `alembic.ini`
- Determine if the app actually uses a database (some apps are stateless and this criterion may not apply)

## Criterion-Specific Verification Steps

- Confirm at least one schema definition mechanism exists: ORM models, Prisma schema, or SQL migration files
- For Prisma: run `npx prisma validate` to confirm the schema is syntactically valid
- For Alembic: run `alembic check` or `alembic heads` to confirm migration chain is intact
- For Django: run `python manage.py showmigrations` and confirm no unapplied migrations
- Verify migration files are committed to version control (not gitignored)
- Check that models/schema files have substantive content (actual tables/columns, not just boilerplate)
