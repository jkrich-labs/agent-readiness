---
signal_name: Release Automation
---

## Criterion-Specific Fix Guidance

- **GitHub Actions CD pipeline**: Create a `.github/workflows/release.yml` or `.github/workflows/deploy.yml` triggered on push to `main`, tag creation, or release publication. The workflow should build, test, and deploy automatically without manual intervention.
- **semantic-release**: Full automation from commit to published release. Install (`npm install --save-dev semantic-release`) and configure `.releaserc.json`. Add a CI job that runs `npx semantic-release` on push to `main`. It auto-bumps versions, creates GitHub releases, and publishes packages.
- **GitOps (ArgoCD/Flux)**: Store Kubernetes manifests or Helm charts in a deployment repo. CI pushes updated manifests (with new image tags) to the GitOps repo, and ArgoCD/Flux automatically syncs the cluster. Configure `argocd-cm` with auto-sync enabled.
- **Docker image publishing**: Build and push Docker images in CI. Use `docker/build-push-action` to push to GitHub Container Registry (`ghcr.io`), Docker Hub, or ECR. Tag images with both the git SHA and semantic version.
- **Python package publishing**: Use `twine` or `flit publish` in CI to publish to PyPI on tag creation. Configure trusted publishers on PyPI for keyless auth from GitHub Actions.
- **npm package publishing**: Use `npm publish` with `NODE_AUTH_TOKEN` in CI, or configure `semantic-release` with `@semantic-release/npm` plugin for automatic publishing.
- **Terraform/IaC automation**: Use `terraform apply -auto-approve` in CD (with proper state locking and plan review). Or use Atlantis/Spacelift for GitOps-style infrastructure deployment.
- **Key principle**: The release process should require zero manual steps after merging to the default branch. Human intervention should only be needed for rollback or emergency scenarios.

## Criterion-Specific Exploration Steps

- Check for deployment/release workflows in `.github/workflows/`: look for jobs that deploy, publish, or release
- Search for `semantic-release`, `release-please`, `changesets`, or `goreleaser` in config files and `package.json`
- Look for Docker publishing: `Dockerfile` combined with a CI step that pushes images
- Check for GitOps config: ArgoCD `Application` manifests, Flux `HelmRelease` or `Kustomization` resources
- Check for platform deployment configs: `vercel.json`, `netlify.toml`, `fly.toml`, `Procfile`
- Review recent releases: `gh release list --limit 5` to see if releases are being created

## Criterion-Specific Verification Steps

- Confirm a CD pipeline exists in `.github/workflows/` that triggers automatically on merge to `main` or on tag/release events
- Verify the pipeline has run recently: `gh run list --workflow=<release-workflow> --limit 5`
- Confirm the pipeline performs the full release cycle (build, test, deploy/publish) without manual steps
