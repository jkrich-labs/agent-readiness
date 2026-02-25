---
signal_name: Secrets Management
---

## Criterion-Specific Fix Guidance

- Ensure secrets are managed through a proper secrets management solution, not hardcoded or stored in plain text.
- **GitHub Actions secrets** (most common for CI/CD): Store secrets via Settings -> Secrets and variables -> Actions. Reference them in workflows as `${{ secrets.MY_SECRET }}`. Never echo or log secret values.
- **Cloud secrets managers** (for application runtime):
  - AWS Secrets Manager or SSM Parameter Store: use `boto3` (Python) or `@aws-sdk/client-secrets-manager` (Node.js)
  - Google Cloud Secret Manager: use `google-cloud-secret-manager` package
  - Azure Key Vault: use `@azure/keyvault-secrets` or `azure-keyvault-secrets`
  - HashiCorp Vault: use `hvac` (Python) or `node-vault` (Node.js)
- **SOPS/age for encrypted config files**: Install `sops` and `age`, generate a key pair, and encrypt sensitive config files:
  ```bash
  age-keygen -o keys.txt
  sops --encrypt --age <public-key> secrets.yaml > secrets.enc.yaml
  ```
  Add `.sops.yaml` to configure which files/keys to encrypt. Commit encrypted files, never plaintext.
- **`.env` properly gitignored**: At minimum, ensure `.env` is in `.gitignore` and secrets are loaded from environment variables at runtime. Use `python-dotenv` (Python) or `dotenv` (Node.js) to load `.env` files locally.
- **Anti-patterns to fix**: Remove hardcoded API keys, passwords, or tokens from source code. Replace them with environment variable references. Remove any `.env` files that are currently tracked in git (`git rm --cached .env`).
- For Kubernetes deployments, use Kubernetes Secrets or external-secrets-operator to sync from a cloud provider.

## Criterion-Specific Exploration Steps

- Check if `.env` is in `.gitignore`
- Search source code for hardcoded secrets: strings that look like API keys, tokens, or passwords (`API_KEY = "sk-..."`, `password = "..."`)
- Check CI workflows for `${{ secrets.* }}` usage
- Look for cloud SDK secret manager imports in the codebase
- Check for `.sops.yaml`, `*.enc.yaml`, `*.enc.json` (SOPS encrypted files)
- Search for `vault`, `ssm`, `secrets_manager`, `keyvault` references in code or config

## Criterion-Specific Verification Steps

- Confirm `.env` is in `.gitignore` and no `.env` files with real secrets are tracked in git
- Verify CI workflows use `${{ secrets.* }}` for sensitive values (not hardcoded)
- Confirm no plaintext secrets exist in source code (run a secret scanner like `gitleaks detect --source .`)
- If using a cloud secrets manager, verify the integration code exists and references the correct secret paths
