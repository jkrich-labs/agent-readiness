---
signal_name: Backlog Health
---

## Criterion-Specific Fix Guidance

- Ensure >70% of open issues have descriptive titles and at least one label, and that <50% of open issues are stale (older than 365 days).
- **Triage existing issues**:
  - Audit all open issues. Close issues that are no longer relevant, duplicates, or have been resolved without being closed.
  - Add labels to unlabeled issues: at minimum a type label (`bug`, `enhancement`, `chore`) and a priority label.
  - Improve vague issue titles to be specific and descriptive (e.g., "Fix bug" -> "Fix null pointer crash in user profile page on empty bio").
- **Close stale issues**: Use a stale bot or manual triage to close issues that have had no activity for over a year.
  - **GitHub Actions stale bot** (`.github/workflows/stale.yml`):
    ```yaml
    name: Close stale issues
    on:
      schedule:
        - cron: "0 0 * * 1"  # Weekly on Monday
    jobs:
      stale:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/stale@v9
            with:
              stale-issue-message: "This issue has been automatically marked as stale due to inactivity. It will be closed in 30 days if no further activity occurs."
              days-before-stale: 180
              days-before-close: 30
              stale-issue-label: "stale"
              exempt-issue-labels: "pinned,keep-open"
    ```
- **Establish ongoing hygiene**: Schedule regular backlog grooming (weekly or biweekly). Add issue templates with required fields to ensure new issues are created with labels and descriptive titles from the start.
- **Bulk operations via CLI**:
  ```bash
  # List issues without labels
  gh issue list --label "" --state open --limit 100
  # Add labels in bulk
  gh issue edit <number> --add-label "bug,priority:medium"
  # Close stale issues
  gh issue close <number> --comment "Closing as stale — reopen if still relevant"
  ```

## Criterion-Specific Exploration Steps

- Count open issues: `gh issue list --state open --limit 1 --json number | jq length` (check the total from `gh issue list --state open --json number --limit 500`)
- Check how many open issues have labels: `gh issue list --state open --limit 500 --json labels,number | jq '[.[] | select(.labels | length > 0)] | length'`
- Check how many issues are older than 365 days: `gh issue list --state open --limit 500 --json createdAt,number`
- Look for an existing stale bot workflow in `.github/workflows/`
- Check issue templates to see if they auto-apply labels

## Criterion-Specific Verification Steps

- Confirm >70% of open issues have at least one label and a descriptive title (more than 5 words)
- Confirm <50% of open issues are older than 365 days
- If a stale bot is configured, verify the workflow runs successfully and has marked or closed stale issues
- Spot-check 10 recent issues to verify they have appropriate labels and clear titles
