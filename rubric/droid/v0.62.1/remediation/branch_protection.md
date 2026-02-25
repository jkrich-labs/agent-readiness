---
signal_name: Branch Protection
---

## Criterion-Specific Fix Guidance

- Enable branch protection rules on the default branch (usually `main` or `master`).
- Use GitHub rulesets (preferred, newer) or legacy branch protection settings.
- **Via GitHub CLI**: `gh api repos/{owner}/{repo}/rulesets -X POST` with a ruleset that requires pull request reviews and status checks to pass.
- **Via GitHub web UI**: Settings → Branches → Add branch protection rule → check "Require a pull request before merging" and "Require status checks to pass before merging".
- At minimum require: 1 approving review, status checks passing, and branch is up to date before merging.
- For legacy branch protection: `gh api repos/{owner}/{repo}/branches/main/protection -X PUT` with appropriate JSON body.

## Criterion-Specific Exploration Steps

- Determine the default branch name: `git symbolic-ref refs/remotes/origin/HEAD`
- Check current branch protection status: `gh api repos/{owner}/{repo}/branches/{branch}/protection` (will 404 if not configured)
- Check for GitHub rulesets: `gh api repos/{owner}/{repo}/rulesets`
- Verify `gh auth status` succeeds (required for API calls)

## Criterion-Specific Verification Steps

- Run `gh api repos/{owner}/{repo}/branches/{branch}/protection` and confirm it returns protection rules (not 404)
- Verify the response includes `required_pull_request_reviews` and `required_status_checks`
