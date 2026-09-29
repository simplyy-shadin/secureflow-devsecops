# SecureFlow DevSecOps

SecureFlow is a hands-on application security and DevSecOps project focused on building security controls into a small web service and its delivery pipeline.

The repository is being developed incrementally. Each control is added through an issue and pull request so the design decisions, failures, fixes, and trade-offs remain visible in the project history.

## Current focus

The first milestone is the project foundation: repository conventions, a minimal API service, containerization, and baseline CI. Security-specific controls such as secret scanning, SAST, dependency analysis, container scanning, and DAST are added after that baseline is stable.

## Application

The project includes a small FastAPI service that exists to give the security pipeline something understandable to build, test, review, and eventually attack in controlled test cases.

Current endpoint:

```text
GET /health
```

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Run the tests with:

```bash
pytest
```

Windows setup and additional notes are in [docs/local-development.md](docs/local-development.md).

## Planned controls

- secret scanning
- static application security testing
- dependency and supply-chain checks
- container image scanning
- dynamic application security testing
- threat modeling and documented security gates

## Project status

Early development. See the open issues for the implementation roadmap.
