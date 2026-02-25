---
signal_name: PR Templates
---

## Criterion-Specific Fix Guidance

- Create a pull request template so every PR starts with a structured description.
- **GitHub**: Create `.github/pull_request_template.md`:
  ```markdown
  ## Summary
  <!-- What does this PR do? Why is it needed? -->

  ## Changes
  -

  ## Test Plan
  - [ ] Unit tests added/updated
  - [ ] Manual testing performed
  - [ ] CI passes

  ## Related Issues
  <!-- Link related issues: Fixes #123, Relates to #456 -->

  ## Screenshots
  <!-- If applicable, add screenshots for UI changes -->
  ```
- **GitLab**: Create `.gitlab/merge_request_templates/Default.md` with similar structure. Multiple templates can be offered by creating additional files in that directory.
- **Multiple templates** (GitHub): Create `.github/PULL_REQUEST_TEMPLATE/` directory with multiple `.md` files. Contributors select a template by appending `?template=filename.md` to the PR URL. Alternatively, a single default template at `.github/pull_request_template.md` is simpler and sufficient for most repos.
- **Key sections to include**:
  - Summary/description of what and why
  - Test plan or verification steps
  - Related issues (with `Fixes #N` syntax for auto-closing)
  - Checklist items for common review concerns (tests, docs, migrations)
- Keep the template concise — a template that is too long will be ignored or deleted by contributors. Aim for 15-30 lines.
- Use HTML comments (`<!-- -->`) for instructional text so they are invisible in the rendered PR description.

## Criterion-Specific Exploration Steps

- Check if `.github/pull_request_template.md` exists (case-insensitive — GitHub accepts various casings)
- Check for `.github/PULL_REQUEST_TEMPLATE/` directory with multiple templates
- Check for GitLab MR templates in `.gitlab/merge_request_templates/`
- Review recent PRs to see if they follow a consistent structure (which may indicate an existing template)

## Criterion-Specific Verification Steps

- Confirm `.github/pull_request_template.md` (or GitLab equivalent) exists
- Verify the template contains at least: a summary section, a test plan or checklist, and a related issues section
- Test by starting a new PR on GitHub and confirming the template auto-populates the description field
- Verify the template is concise and uses HTML comments for instructions
