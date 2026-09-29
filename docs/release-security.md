# Release image integrity

SecureFlow separates ordinary pull-request validation from container-image publishing.

The release workflow in `.github/workflows/release-image.yml` is designed around two trust levels:

1. pull requests may build the release candidate and generate a software bill of materials (SBOM), but receive no package-publishing or signing permissions;
2. version-tag events may publish the image and create attestations.

This prevents an ordinary pull request from gaining registry-write or signing capability merely because it exercises the release build.

## Pull-request validation

Changes that affect the release image run a non-publishing validation job.

The job:

- builds the repository Dockerfile locally;
- generates a CycloneDX SBOM with the pinned Trivy version;
- verifies that the SBOM parses as JSON, declares `CycloneDX`, and contains components;
- retains the SBOM as a short-lived workflow artifact.

The validation step is deliberately useful without registry credentials. It catches broken release builds and broken SBOM generation before a release tag exists.

## Release trigger

Publishing is restricted to Git tags matching the workflow's `v*` trigger and an additional shell validation that requires:

```text
vMAJOR.MINOR.PATCH
```

For example:

```text
v0.1.0
```

A tag that reaches the workflow but does not match that version format fails before registry authentication or publishing.

## Registry authentication

The workflow authenticates to GitHub Container Registry with the workflow-scoped GitHub token.

No long-lived registry password, personal access token, or Docker credential is stored in the repository.

The publish job alone receives:

- `packages: write`
- `id-token: write`
- `attestations: write`
- `artifact-metadata: write`

The workflow-level default remains `contents: read`.

## Immutable image identity

The release job publishes two human-readable tags:

```text
ghcr.io/simplyy-shadin/secureflow-devsecops:vMAJOR.MINOR.PATCH
ghcr.io/simplyy-shadin/secureflow-devsecops:sha-<12-character-commit>
```

Neither tag is treated as the security identity of the artifact.

After the push, Buildx metadata is used to capture the registry-provided SHA-256 image digest. The workflow verifies that the pushed image can be resolved by that digest.

The immutable reference therefore has the form:

```text
ghcr.io/simplyy-shadin/secureflow-devsecops@sha256:<digest>
```

That digest is also written to `release-metadata.json`.

## SBOM

The release job runs Trivy against the published image digest, not merely against the source tree or a mutable image tag.

The result is:

```text
secureflow-release-sbom.cdx.json
```

The SBOM is validated before attestation and retained with the release metadata as workflow evidence.

This allows a reviewer to tie the component inventory to the exact published image digest.

## Signed attestations

The release workflow uses GitHub's attestation action with short-lived OIDC-backed signing.

Two attestations are produced for the same OCI image digest:

- SLSA build provenance;
- CycloneDX SBOM attestation.

Both are pushed to the registry and associated with the GitHub repository.

The workflow pins the attestation action to an immutable commit SHA rather than a floating action tag.

## Verification

Use the immutable image reference recorded by the workflow.

After authenticating to GHCR when required, build provenance can be verified with GitHub CLI:

```bash
gh attestation verify \
  oci://ghcr.io/simplyy-shadin/secureflow-devsecops@sha256:<digest> \
  --repo simplyy-shadin/secureflow-devsecops
```

The CycloneDX SBOM attestation can be selected explicitly:

```bash
gh attestation verify \
  oci://ghcr.io/simplyy-shadin/secureflow-devsecops@sha256:<digest> \
  --repo simplyy-shadin/secureflow-devsecops \
  --predicate-type https://cyclonedx.org/bom
```

Verification should use the digest rather than a mutable tag.

## Evidence retained by the workflow

For a versioned release, the workflow retains:

- the CycloneDX SBOM;
- `release-metadata.json`, containing the image, digest, immutable reference, version tag, source commit and workflow-run URL;
- GitHub-hosted signed attestation records;
- registry-attached provenance and SBOM attestations.

The JSON evidence artifact is retained for 30 days. Attestation retention follows the repository and registry services rather than the short-lived Actions artifact policy.

## Remaining Kubernetes follow-up

PR #22 intentionally left `CKV_K8S_43` skipped because no real SecureFlow image digest existed at that point.

This release workflow removes the reason for inventing a digest, but the exception should not be deleted until a real version tag successfully publishes the first image.

After that release:

1. obtain the published SHA-256 digest from `release-metadata.json`;
2. update `deploy/k8s/deployment.yaml` to use the immutable GHCR digest;
3. remove the `CKV_K8S_43` skip annotation;
4. run Checkov again and require zero skipped image-digest checks.

That follow-up converts the documented residual risk into a verifiable deployment control rather than changing the manifest before an artifact actually exists.

## Limitations

A signed attestation proves statements about an artifact and its build identity; it does not prove that the application is vulnerability-free.

The release pipeline therefore complements, rather than replaces:

- Gitleaks;
- Semgrep;
- Trivy dependency and image vulnerability scanning;
- Checkov;
- OWASP ZAP;
- threat modeling and review.

The current release build targets `linux/amd64`. Multi-platform release publishing is intentionally deferred until it is needed, because each additional platform would create another image manifest and testing surface.
