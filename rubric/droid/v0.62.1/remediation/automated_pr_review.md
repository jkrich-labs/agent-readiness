---
signal_name: Automated PR Review
---

## Criterion-Specific Fix Guidance

- **Danger.js**: Install Danger (`npm install --save-dev danger`) and create a `dangerfile.ts` or `dangerfile.js` at the repo root. Configure rules to check PR size, missing tests, CHANGELOG updates, etc. Add a CI step: `npx danger ci` with `DANGER_GITHUB_API_TOKEN` set.
- **GitHub Actions bot reviews**: Use actions like `github/codeql-action` for security review, `reviewdog/action-eslint` for lint comments on PRs, or `coverbot` for coverage change comments.
- **AI-powered review**: Configure tools like CodeRabbit (`.coderabbit.yaml`), Sourcery (`.sourcery.yaml`), or Droid to automatically review PRs. These post inline comments on code changes.
- **Custom GitHub Actions**: Create a workflow triggered on `pull_request` that runs analysis and posts review comments via `gh pr review` or the GitHub API (`POST /repos/{owner}/{repo}/pulls/{number}/reviews`).
- **Reviewdog**: Install reviewdog and configure it to annotate PRs with lint/analysis results. Example: `reviewdog -reporter=github-pr-review` in CI.
- **Minimum viable setup**: A workflow that runs linters and posts results as PR review comments is sufficient. Example: use `actions/github-script` to post a comment summarizing lint findings.

## Criterion-Specific Exploration Steps

- Check for `dangerfile.ts`, `dangerfile.js`, or `dangerfile.rb` at the repo root
- Search CI workflows for `danger ci`, `reviewdog`, `coderabbit`, `sourcery`, or PR review actions
- Look for `.coderabbit.yaml`, `.sourcery.yaml`, or similar bot config files
- Check if any workflow runs on the `pull_request` event and uses `gh pr review` or `github-script` to post comments
- Check `package.json` devDependencies for `danger`

## Criterion-Specific Verification Steps

- Confirm at least one mechanism exists: Danger config file, reviewdog in CI, AI review bot config, or a custom PR comment workflow
- Open a test PR and verify that automated comments appear on the PR
- Check recent merged PRs for bot-generated review comments: `gh pr list --state merged --limit 5 --json number,reviews`
