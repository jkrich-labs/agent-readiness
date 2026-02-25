---
signal_name: Service Flow Documented
---

## Criterion-Specific Fix Guidance

- Add architecture diagrams using **Mermaid** (renders natively in GitHub Markdown) or **PlantUML** (`.puml` files).
- **Mermaid in Markdown**: Embed diagrams directly in `README.md`, `docs/architecture.md`, or `AGENTS.md` using fenced code blocks with the `mermaid` language tag.
- Diagram should show: service boundaries, data flow direction, external dependencies (databases, caches, queues, third-party APIs), and communication protocols (REST, gRPC, events).
- **Minimal example** for a typical web app:
  ```mermaid
  graph LR
    Client --> Frontend
    Frontend --> API
    API --> Database
    API --> Cache[(Redis)]
  ```
- For microservices or multi-app repos, create a `docs/architecture.md` with a system-level diagram and per-service diagrams.
- **PlantUML alternative**: Create `.puml` files in a `docs/` directory. Add a CI step to render them to SVG/PNG using `plantuml` CLI or a GitHub Action like `grassedge/generate-plantuml-action`.
- Document service dependencies in a structured format: a `docs/services.md` table listing each service, its purpose, port, and upstream/downstream dependencies.
- For simpler repos (single service), a data-flow or component diagram in the README is sufficient.

## Criterion-Specific Exploration Steps

- Search for existing diagrams: `*.puml`, `*.plantuml`, `*.mmd`, `*.mermaid`, or Mermaid blocks in Markdown files
- Check `docs/` directory for architecture documentation
- Look at `docker-compose.yml` or Kubernetes manifests to understand service topology
- Review `README.md` and `AGENTS.md` for any existing architecture descriptions
- Check for infrastructure-as-code files (`terraform/`, `cdk/`, `pulumi/`) that reveal service dependencies

## Criterion-Specific Verification Steps

- Confirm at least one architecture diagram exists (Mermaid block in a `.md` file or a `.puml`/`.mermaid` file in the repo)
- Verify the diagram references actual services/components from the codebase (not a generic placeholder)
- If using Mermaid in Markdown, confirm it renders correctly on GitHub by viewing the file in the GitHub web UI
