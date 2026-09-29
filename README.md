# SecureFlow DevSecOps

SecureFlow is a hands-on application security and DevSecOps project focused on building security controls into a small web service and its delivery pipeline.

The repository is developed incrementally. Each control is added through an issue and pull request so design decisions, failures, fixes, and trade-offs remain visible in the project history.

## Current application

SecureFlow currently provides a small FastAPI service with registration and short-lived Bearer-token authentication.

Available endpoints:

```text
GET  /health
POST /auth/register
POST /auth/login
GET  /users/me
```

Passwords are stored as Argon2id hashes. JWT signing material is supplied through environment configuration rather than committed to the repository. Authentication design notes are in [docs/authentication.md](docs/authentication.md).

## Local setup

Create and activate a Python virtual environment, then install the development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Copy `.env.example` to `.env` and generate a local JWT signing key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Place the generated value after `JWT_SECRET_KEY=` in the ignored `.env` file, then start the service:

```bash
uvicorn app.main:app --reload
```

Run the tests with:

```bash
pytest
```

Windows setup and additional details are in [docs/local-development.md](docs/local-development.md).

## Current engineering controls

- issue and pull-request based development
- Python linting and automated tests in GitHub Actions
- Gitleaks secret scanning with a controlled detection self-test and Git-history scan
- Semgrep SAST with a community Python baseline, tested project-owned rules, a blocking high-confidence gate, and SARIF output
- non-root container runtime
- read-only container root filesystem
- dropped Linux capabilities and `no-new-privileges`
- persistent SQLite data isolated to a dedicated container volume
- container smoke testing for registration, login, authenticated access, and restart persistence

Secret-scanning behavior and finding-response policy are documented in [docs/secret-scanning.md](docs/secret-scanning.md). Static-analysis rules, gate behavior, and limitations are documented in [docs/static-analysis.md](docs/static-analysis.md).

## Planned security controls

- dependency and supply-chain checks
- container image scanning
- dynamic application security testing
- threat modeling and documented security gates

See the open issues for the implementation roadmap.
