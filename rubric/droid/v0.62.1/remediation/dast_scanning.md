---
signal_name: DAST Scanning
---

## Criterion-Specific Fix Guidance

- **OWASP ZAP in CI (GitHub Actions)**: Add the ZAP GitHub Action to your CI pipeline. For a baseline scan: `- uses: zaproxy/action-baseline@v0.10.0; with: { target: 'http://localhost:8080' }`. For a full scan: `- uses: zaproxy/action-full-scan@v0.9.0`. Start your application in a previous step using `docker-compose up -d` or `npm start &`, then wait for it to be ready before scanning.
- **OWASP ZAP with Docker**: Run ZAP as a Docker container in CI: `docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://target:8080 -r report.html`. Upload `report.html` as a CI artifact. Configure scan rules in a `zap-rules.tsv` file to suppress false positives.
- **Nuclei (fast vulnerability scanner)**: Install Nuclei or use the Docker image: `docker run projectdiscovery/nuclei -u http://localhost:8080 -t cves/ -t exposures/ -t misconfiguration/ -o results.txt`. Nuclei uses community-maintained templates for known CVEs and misconfigurations. Add as a CI step with `--severity medium,high,critical` to filter noise.
- **StackHawk (commercial DAST)**: Sign up at stackhawk.com, create a `stackhawk.yml` configuration file: `app: { applicationId: "...", env: CI, host: "http://localhost:8080" }`. Add to CI: `- uses: stackhawk/hawkscan-action@v2.1.0`. StackHawk integrates with GitHub PRs and provides actionable findings.
- **DAST scan target**: The application must be running during DAST scanning. In CI, start the app in the background, wait for readiness (poll the health endpoint), then run the scanner. Use `docker-compose` or `docker run -d` to start the app with its dependencies.
- **Authentication for protected routes**: Configure the DAST scanner with authentication credentials to scan routes behind login. In ZAP, use the authentication context configuration. In StackHawk, use the `authentication` section of `stackhawk.yml`. Without auth, the scanner only tests public endpoints.
- **Handling findings**: Set the scan to fail the build only on high/critical findings initially. As the team matures, lower the threshold. Use a `zap-rules.tsv` or tool-specific suppression file to manage accepted risks and false positives.
- **API scanning**: For API-only services, provide the OpenAPI spec to the DAST tool for API-aware scanning. ZAP: `zap-api-scan.py -t openapi.yaml -f openapi`. Nuclei: use API-specific templates.

## Criterion-Specific Exploration Steps

- Check CI workflows for DAST scanning steps: `grep -rn 'zaproxy\|zap-baseline\|nuclei\|hawkscan\|burp\|dast' .github/workflows/`
- Look for DAST configuration files: `stackhawk.yml`, `zap-rules.tsv`, `.zap/`, `nuclei-config.yaml`
- Check for Docker Compose or app startup in CI that would support running the app for scanning
- Search for security scanning in general: `grep -rn 'security.*scan\|vulnerability.*scan\|pen.*test' .github/workflows/ docs/`
- Check if the app has a health endpoint that a CI step could poll for readiness before scanning
- Look for an OpenAPI spec that could be fed to the DAST scanner for API-aware testing

## Criterion-Specific Verification Steps

- Confirm a DAST scanning step exists in a CI workflow and is not disabled or commented out
- Verify the scan runs against a live instance of the application (not just static files)
- Check that the scan produces a report (HTML, JSON, or SARIF) that is either uploaded as an artifact or posted to GitHub Code Scanning
- Run the DAST scan locally: `docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://localhost:8080` and verify it completes
- Confirm the CI pipeline fails (or at least warns) on high-severity findings
- Verify authenticated routes are covered if the application has authentication
