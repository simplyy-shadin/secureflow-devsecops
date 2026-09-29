# Container security baseline

The container definition is intentionally small and restrictive. Security scanning validates this baseline rather than replacing it with a scanner-specific example.

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

### Runtime package-management reduction

Python dependencies are installed during the image build, then pip is removed from the final runtime filesystem. The application does not need package-management tooling after startup.

The supply-chain workflow verifies that pip is absent from the built image before running the final vulnerability gate.

### Base-image pinning

The Dockerfile keeps the readable `python:3.12-slim` tag but also pins the resolved OCI digest. This prevents an unchanged Dockerfile from silently resolving to different base-image contents.

Updating the base image is an explicit maintenance action:

1. resolve and review the new `python:3.12-slim` digest
2. update the Dockerfile in a pull request
3. rebuild the image
4. run container smoke tests and Trivy scanning
5. merge only after the new image satisfies the same gates

### Health check

The image performs an HTTP request against `/health` using Python's standard library. This avoids adding tools such as curl only for health checking.

## Database lifecycle

For the current development stage, the FastAPI lifespan handler creates missing SQLAlchemy tables on application startup. This keeps the local demo self-contained while the schema is still small.

This is not being treated as a production migration strategy. Once the schema starts evolving, explicit migrations should replace startup-time table creation so schema changes are versioned and reviewable.

## Known trade-offs

The current Compose database is SQLite backed by a Docker named volume. That is suitable for this single-service portfolio environment, but it is not a substitute for a production database service.

A pinned base-image digest improves reproducibility but does not update itself. The digest must be reviewed periodically so security fixes in newer Python/Debian images are not missed.

Container hardening controls do not prove the image is vulnerability-free. Trivy scanning, smoke tests, and periodic dependency/base-image maintenance remain separate controls.
