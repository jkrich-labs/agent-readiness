---
signal_name: Issue Templates
---

## Criterion-Specific Fix Guidance

- Create issue templates in `.github/ISSUE_TEMPLATE/` (GitHub) or `.gitlab/issue_templates/` (GitLab).
- **GitHub — create at least two templates**:
  - `.github/ISSUE_TEMPLATE/bug_report.yml` (YAML form format, preferred):
    ```yaml
    name: Bug Report
    description: Report a bug or unexpected behavior
    labels: ["bug", "triage"]
    body:
      - type: textarea
        id: description
        attributes:
          label: Bug Description
          description: What happened? What did you expect?
        validations:
          required: true
      - type: textarea
        id: steps
        attributes:
          label: Steps to Reproduce
          description: How can we reproduce the issue?
        validations:
          required: true
      - type: textarea
        id: environment
        attributes:
          label: Environment
          description: OS, runtime version, browser, etc.
    ```
  - `.github/ISSUE_TEMPLATE/feature_request.yml`:
    ```yaml
    name: Feature Request
    description: Suggest a new feature or improvement
    labels: ["enhancement"]
    body:
      - type: textarea
        id: problem
        attributes:
          label: Problem
          description: What problem does this solve?
        validations:
          required: true
      - type: textarea
        id: solution
        attributes:
          label: Proposed Solution
          description: How should this work?
    ```
- **Add a config file** to control blank issue creation (`.github/ISSUE_TEMPLATE/config.yml`):
  ```yaml
  blank_issues_enabled: false
  contact_links:
    - name: Questions
      url: https://github.com/org/repo/discussions
      about: Ask questions in Discussions
  ```
- **GitLab**: Create `.gitlab/issue_templates/Bug.md` and `.gitlab/issue_templates/Feature.md` with Markdown templates using headings for each section.
- Older Markdown format (`.github/ISSUE_TEMPLATE/bug_report.md`) also works but YAML forms provide better UX with dropdowns and required fields.

## Criterion-Specific Exploration Steps

- Check if `.github/ISSUE_TEMPLATE/` or `.gitlab/issue_templates/` directory exists
- Look for legacy single-file template: `.github/ISSUE_TEMPLATE.md`
- Check if `.github/ISSUE_TEMPLATE/config.yml` exists
- Review existing templates for completeness (do they have required fields? labels? useful prompts?)

## Criterion-Specific Verification Steps

- Confirm `.github/ISSUE_TEMPLATE/` directory exists with at least one template file (`.yml` or `.md`)
- Verify templates are valid YAML (for `.yml` files) or valid Markdown (for `.md` files)
- Check that templates include meaningful prompts and required fields, not just empty headings
- Test by clicking "New Issue" on GitHub and confirming the template chooser appears
