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

Start the API:

```bash
uvicorn app.main:app --reload
```

The service listens on `http://127.0.0.1:8000`. The health endpoint is available at `/health`.

Run the tests:

```bash
pytest
```

## Secrets

Use `.env.example` only as a reference. Local `.env` files are ignored by Git and must not contain credentials that are also used anywhere outside the local test environment.
