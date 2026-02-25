---
signal_name: Issue Labeling System
---

## Criterion-Specific Fix Guidance

- Establish a consistent label taxonomy covering three dimensions: **priority**, **type**, and **area**.
- **Priority labels** (use color coding for visual clarity):
  - `priority:critical` (red) — production outage, data loss, security vulnerability
  - `priority:high` (orange) — major functionality broken, blocking work
  - `priority:medium` (yellow) — important but not blocking
  - `priority:low` (blue) — nice to have, minor improvements
- **Type labels**:
  - `bug` — something is broken
  - `enhancement` or `feature` — new functionality
  - `chore` or `maintenance` — refactoring, dependency updates, CI changes
  - `documentation` — doc improvements
  - `question` — needs clarification or discussion
- **Area labels** (repo-specific):
  - `area:frontend`, `area:backend`, `area:api`, `area:infra`, `area:ci`, etc.
  - Match these to the repo's actual code areas and team ownership
- **Create labels via GitHub CLI**:
  ```bash
  gh label create "priority:critical" --color "B60205" --description "Production outage or security vulnerability"
  gh label create "priority:high" --color "D93F0B" --description "Major functionality broken"
  gh label create "bug" --color "d73a4a" --description "Something is broken"
  gh label create "enhancement" --color "a2eeef" --description "New feature or improvement"
  gh label create "area:backend" --color "0075ca" --description "Backend code changes"
  ```
- **Automate labeling**: Add a GitHub Action like `actions/labeler` that auto-labels PRs based on changed file paths, or use `github/issue-labeler` to auto-label issues based on title/body keywords.
- Document the labeling system in `CONTRIBUTING.md` so contributors know which labels to apply.

## Criterion-Specific Exploration Steps

- List existing labels: `gh label list --limit 100`
- Check if labels follow a consistent naming convention (e.g., `type:bug` vs just `bug`)
- Look for label automation in `.github/labeler.yml` or `.github/workflows/` that apply labels automatically
- Check `CONTRIBUTING.md` for documented labeling guidelines
- Review recent issues to see if labels are actually being applied consistently

## Criterion-Specific Verification Steps

- Confirm labels exist for at least two of the three categories: priority, type, and area
- Verify labels have descriptions (not just names) so their purpose is clear
- Check that recent issues (last 10-20) have at least one label applied
- If label automation exists, verify the configuration matches the current repo structure
