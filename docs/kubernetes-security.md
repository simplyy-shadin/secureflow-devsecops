# Kubernetes security baseline

SecureFlow includes a Kubernetes reference deployment under `deploy/k8s/`. The goal is to carry the runtime controls already enforced by Docker Compose into an orchestrated environment and make the manifests subject to a separate IaC security gate.

## Runtime controls

The Deployment currently enforces:

- dedicated `secureflow` namespace
- dedicated service account with token automount disabled
- non-root execution as UID/GID `10001`
- `RuntimeDefault` seccomp
- read-only container root filesystem
- all Linux capabilities dropped
- privilege escalation disabled
- explicit CPU and memory requests/limits
- readiness and liveness probes
- in-memory writable `/tmp`
- writable application data isolated to `/data`
- ClusterIP-only Service
- NetworkPolicy with explicit ingress and no application egress

The Dockerfile uses the same deterministic UID/GID `10001`, so the image metadata and Kubernetes security context do not rely on different user identities.

## Secret handling

Kubernetes does not inject JWT signing material through an environment variable.

The Deployment expects a Secret named `secureflow-runtime` with a `jwt-secret-key` entry. Kubernetes mounts that entry read-only at:

```text
/var/run/secrets/secureflow/jwt-secret-key
```

The container receives only:

```text
JWT_SECRET_KEY_FILE=/var/run/secrets/secureflow/jwt-secret-key
```

SecureFlow validates that exactly one signing-key source is configured: `JWT_SECRET_KEY` or `JWT_SECRET_KEY_FILE`. File-backed keys are read at runtime and must contain at least 32 characters.

No Secret object containing signing material is committed to the repository.

## Persistence model

The current application still uses SQLite. Kubernetes therefore runs one replica with a `Recreate` deployment strategy and a `ReadWriteOnce` PVC.

This is deliberate rather than an availability claim. The manifest is not a high-availability database design. A multi-replica production deployment would require moving persistence to a database designed for concurrent networked clients and replacing startup-time schema creation with migrations.

## Network boundary

The Service is `ClusterIP`; no public Ingress or LoadBalancer is defined.

The NetworkPolicy allows TCP/8000 ingress only from pods carrying:

```text
secureflow-access: allowed
```

and denies application egress.

A future ingress controller, service mesh, monitoring agent, external database, or telemetry service would require explicit NetworkPolicy changes. TLS termination and HSTS remain outside this reference manifest.

## Checkov gate

The IaC workflow installs Checkov `3.3.20` from its published Linux release ZIP and verifies the archive SHA-256 before execution.

The workflow also creates a temporary privileged Pod manifest and verifies that Checkov rejects it with `CKV_K8S_16`. The control file exists only on the GitHub Actions runner.

The first observation scan produced:

```text
Passed checks: 89
Failed checks: 3
Skipped checks: 0
```

The findings were:

| Check | Finding | Resolution |
| --- | --- | --- |
| `CKV_K8S_15` | Image pull policy was `IfNotPresent` | Changed to `Always` |
| `CKV_K8S_35` | JWT Secret was exposed through an environment-variable reference | Added file-backed signing-key support and mounted the Secret read-only |
| `CKV_K8S_43` | Application image was not digest-pinned | Explicit temporary exception; see below |

The first remediation pass intentionally left `CKV_K8S_43` skipped until a real SecureFlow image existed:

```text
Passed checks: 91
Failed checks: 0
Skipped checks: 1
```

Release `v0.1.0` subsequently published the application image from source commit `e89251f71695d15f78ed888d59921b49cc46b839`. The release workflow recorded the registry-provided digest:

```text
sha256:93a26b7b9d665574026e9dd850a75670363f97dfacda4c736babc307ab80d32c
```

The Deployment now uses:

```text
ghcr.io/simplyy-shadin/secureflow-devsecops@sha256:93a26b7b9d665574026e9dd850a75670363f97dfacda4c736babc307ab80d32c
```

The temporary `CKV_K8S_43` exception has therefore been removed. The IaC workflow remains blocking and retains its JSON report for 14 days.

## Deployment prerequisites

This directory is a security-reviewed reference baseline, not a claim that a cluster has already been provisioned.

Before applying it:

1. verify the published SecureFlow image provenance for the digest referenced by the Deployment;
2. create the `secureflow-runtime` Secret out of band with a generated signing key;
3. confirm the cluster storage class supports the PVC;
4. confirm the NetworkPolicy matches the intended ingress path.
