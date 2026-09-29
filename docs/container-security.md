# Container security baseline

The first container definition is intentionally small and restrictive. Later security scanning work will validate this baseline rather than replacing it with a scanner-specific example.

## Current controls

### Non-root runtime

The image creates a dedicated `secureflow` user and switches to it before the application starts. The service does not require root privileges.

### Reduced build context

`.dockerignore` prevents Git metadata, local virtual environments, test output, scan reports, and local environment files from being copied into the Docker build context.

### Read-only runtime

The local Compose configuration uses a read-only root filesystem. A temporary filesystem is mounted at `/tmp` for libraries that may need transient writable space.

### Capability reduction

The container drops all Linux capabilities and enables `no-new-privileges`. The current API does not require additional capabilities.

### Health check

The image performs an HTTP request against `/health` using Python's standard library. This avoids adding tools such as curl only for health checking.

## Known trade-offs

The base image currently uses the `python:3.12-slim` tag. This is easy to read and maintain during the early project stages, but a mutable tag does not provide full build reproducibility. A later supply-chain hardening task can pin the image by digest and document the update process.

The container configuration is not treated as secure merely because these controls exist. Trivy and configuration scanning will be added separately and may produce findings that require changes to this baseline.
