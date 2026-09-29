# Local security validation

This guide reproduces the main SecureFlow security checks from a developer workstation. CI remains the authoritative automated gate, but these commands are useful before opening a pull request and for demonstrating how each control behaves.

For closest CI parity, use the scanner versions pinned in the workflows:

- Gitleaks 8.30.1
- Semgrep 1.178.0
- Trivy 0.70.0
- Checkov 3.3.20

A newer local scanner can produce different advisory or rule output because vulnerability databases and rules evolve independently.

## 1. Application checks

Activate the project virtual environment and run:

```bash
ruff check app tests
pytest -q
```

The application tests cover registration, authentication, JWT validation, security headers, database behavior and the user model.

## 2. Container runtime

Create a local `.env` from `.env.example`, generate a development-only JWT signing key, then build and start the application:

```bash
docker compose up --build -d
docker compose ps
```

The service should become healthy on `http://127.0.0.1:8000`.

### Non-root user

```bash
docker compose exec api id
```

The runtime UID/GID should be `10001`, not root.

### Read-only root filesystem

PowerShell:

```powershell
$container = docker compose ps -q api
docker inspect --format '{{.HostConfig.ReadonlyRootfs}}' $container
```

Expected result:

```text
true
```

A write under `/app` should fail:

```bash
docker compose exec api sh -c "touch /app/test-file"
```

A write under the dedicated data mount should succeed:

```bash
docker compose exec api sh -c "touch /data/test-file && ls -l /data/test-file"
docker compose exec api rm /data/test-file
```

### Runtime package-manager reduction

```bash
docker compose exec api python -c "import importlib.util; print(importlib.util.find_spec('pip'))"
```

Expected result:

```text
None
```

### Persistence

Register a test user through `/docs` or the API, restart the service, then confirm the same credentials still work:

```bash
docker compose restart api
docker compose ps
```

A duplicate registration for the same email should return `409 Conflict`, proving the SQLite data survived the container restart.

## 3. Gitleaks

Scan reachable Git history:

```bash
gitleaks git --config .gitleaks.toml --redact --verbose --log-opts="--all" .
```

A clean repository scan should report no leaks. CI additionally runs a generated fake-secret control to prove the scanner blocks credential-shaped data.

## 4. Semgrep

Run the project-owned rule tests:

```bash
semgrep --test security/semgrep
```

Then scan the application with the same blocking configuration used in CI:

```bash
semgrep scan --config p/python --config security/semgrep/secureflow.yml --severity ERROR --error app
```

The custom rules cover prohibited `shell=True` subprocess usage and Python pickle deserialization.

## 5. Trivy dependency scan

```bash
trivy fs --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed .
```

This checks the dependency state for actionable HIGH/CRITICAL known vulnerabilities.

## 6. Trivy container scan

The Compose build creates the local image `secureflow-devsecops-api` by default:

```bash
trivy image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed secureflow-devsecops-api
```

Use `docker images` if the local image name differs.

## 7. CycloneDX SBOM

Generate a local SBOM from the built image:

```bash
trivy image --format cyclonedx --output secureflow-local-sbom.cdx.json secureflow-devsecops-api
```

Confirm the document contains `"bomFormat": "CycloneDX"` and component entries. This file is local evidence; the release workflow separately generates and attests an SBOM against the published immutable image digest.

## 8. Checkov Kubernetes IaC

```bash
checkov --directory deploy/k8s --framework kubernetes --compact
```

The current manifests are expected to pass without policy skips, including the immutable image-digest rule.

## 9. OWASP ZAP baseline

Keep SecureFlow running and scan the Swagger surface.

PowerShell:

```powershell
docker run --rm -t `
  -v "${PWD}/.zap:/zap/wrk:rw" `
  ghcr.io/zaproxy/zaproxy:stable `
  zap-baseline.py `
  -t http://host.docker.internal:8000/docs `
  -c /zap/wrk/rules.tsv `
  -r zap-report.html `
  -J zap-report.json `
  -w zap-report.md
```

The expected policy outcome is:

- no `FAIL` findings;
- documented Swagger/development findings remain visible as `WARN`;
- scanner classifications such as cacheability remain visible as `INFO`.

See [dast-remediation.md](dast-remediation.md) for the rationale behind the current ZAP policy.

## 10. Clean up

```bash
docker compose down --volumes
```

Generated local SBOM and ZAP report files are ignored by Git and should not be committed as source.
