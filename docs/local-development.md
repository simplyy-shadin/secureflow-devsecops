# Local development

## Requirements

- Python 3.12 or later
- pip

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the development dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Generate a local JWT signing key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the generated value after `JWT_SECRET_KEY=` in `.env`. The key must be at least 32 characters and must not be committed to Git.

Start the API:

```bash
uvicorn app.main:app --reload
```

The service listens on `http://127.0.0.1:8000`. The health endpoint is available at `/health`.

Run the tests:

```bash
pytest
```

## Containers

Docker Compose also requires `JWT_SECRET_KEY`. If a local `.env` file contains the generated key, Compose reads it automatically.

```bash
docker compose up --build
```

The application root filesystem remains read-only. SQLite data is persisted separately in the `secureflow-data` named volume.

## Secrets

Use `.env.example` only as a reference. Local `.env` files are ignored by Git and must not contain credentials that are also used anywhere outside the local development environment.
