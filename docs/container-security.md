# Container security baseline

The first container definition is intentionally small and restrictive. Later security scanning work will validate this baseline rather than replacing it with a scanner-specific example.

## Current controls

### Non-root runtime

The image creates a dedicated `secureflow` user and switches to it before the application starts. The service does not require root privileges.

The image also creates `/data` and assigns it to the same non-root user. This directory is the only persistent writable location used by the application in the Compose deployment.

### Reduced build context

`.dockerignore` prevents Git metadata, local virtual environments, test output, scan reports, and local environment files from being copied into the Docker build context.

### Read-only runtime

The local Compose configuration keeps the container root filesystem read-only. A temporary filesystem is mounted at `/tmp` for transient writes.

Application data is not written back into the image filesystem. Compose mounts the named volume `secureflow-data` at `/data` and sets:

```text
DATABASE_URL=sqlite:////data/secureflow.db
```

This allows SQLite persistence while preserving the read-only root filesystem.

### Capability reduction

The container drops all Linux capabilities and enables `no-new-privileges`. The current API does not require additional capabilities.

### Health check

The image performs an HTTP request against `/health` using Python's standard library. This avoids adding tools such as curl only for health checking.

## Database lifecycle

For the current development stage, the FastAPI lifespan handler creates missing SQLAlchemy tables on application startup. This keeps the local demo self-contained while the schema is still small.

This is not being treated as a production migration strategy. Once the schema starts evolving, explicit migrations should replace startup-time table creation so schema changes are versioned and reviewable.

## Known trade-offs

The base image currently uses the `python:3.12-slim` tag. This is easy to read and maintain during the early project stages, but a mutable tag does not provide full build reproducibility. A later supply-chain hardening task can pin the image by digest and document the update process.

The current Compose database is SQLite backed by a Docker named volume. That is suitable for this single-service portfolio environment, but it is not a substitute for a production database service.

The container configuration is not treated as secure merely because these controls exist. Trivy and configuration scanning will be added separately and may produce findings that require changes to this baseline.
