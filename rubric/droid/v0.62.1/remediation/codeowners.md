---
signal_name: Code Owners
---

## Criterion-Specific Fix Guidance

- Create a `CODEOWNERS` file in the repository root or `.github/CODEOWNERS` (GitHub convention) or `.gitlab/CODEOWNERS` (GitLab convention).
- **Format**: Each line is a file pattern followed by one or more owners (GitHub usernames or team names):
  ```
  # Default owner for everything
  * @org/engineering-team

  # Frontend code
  frontend/  @org/frontend-team
  *.tsx      @org/frontend-team
  *.css      @org/frontend-team

  # Backend code
  backend/   @org/backend-team
  *.py       @org/backend-team

  # Infrastructure
  .github/   @org/platform-team
  terraform/ @org/platform-team
  Dockerfile @org/platform-team

  # Critical configs require senior review
  .env.example @org/tech-leads
  ```
- Use **team mentions** (e.g., `@org/team-name`) rather than individual usernames where possible — teams are easier to maintain as people change roles.
- Ensure referenced teams and users actually exist in the GitHub organization, otherwise CODEOWNERS rules will be silently ignored.
- Order matters: later rules override earlier ones for the same file. Put the most general rules first and specific overrides later.
- Enable "Require review from Code Owners" in branch protection settings to enforce CODEOWNERS-based review requirements.

## Criterion-Specific Exploration Steps

- Check if `CODEOWNERS`, `.github/CODEOWNERS`, or `docs/CODEOWNERS` already exists
- Identify the main code areas/directories and which teams own them
- Check branch protection settings for "Require review from Code Owners" requirement
- Look at recent PR review patterns to understand who typically reviews what

## Criterion-Specific Verification Steps

- Confirm `CODEOWNERS` file exists in one of the standard locations (root, `.github/`, or `docs/`)
- Verify the file contains at least one rule with a valid owner pattern
- Verify referenced GitHub teams or users exist (invalid owners cause rules to be silently ignored)
- Check that the `*` wildcard (catch-all) rule is present so all files have an assigned owner
