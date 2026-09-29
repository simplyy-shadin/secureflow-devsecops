# Security gate model

SecureFlow uses several independent checks rather than treating one scanner as proof that the application is secure. Each workflow has a defined blocking threshold so a finding is not made non-blocking simply to obtain a green build.

## Gate semantics

- **PASS** — the control completed successfully and no finding met its blocking threshold.
- **WARN / observation** — the control produced a finding that remains visible but is not currently a merge blocker. The rationale must be documented and revisited if the affected surface changes.
- **FAIL** — the workflow or scanner failed, or a finding met the control's blocking threshold.

A non-blocking result is not the same as a fixed vulnerability. Reports are retained where useful so lower-severity or contextual findings remain reviewable.

## Current gates

| Control | What it validates | Blocking condition | Evidence |
| --- | --- | --- | --- |
| CI | Ruff, pytest, container runtime behavior, registration/login/profile flow, restart persistence | Lint/test failure, container startup failure, runtime-hardening regression, or failed smoke assertion | Workflow logs |
| Gitleaks | Current repository and Git history | Any detected credential/secret, scanner failure, or failure of the generated fake-secret self-test | Redacted workflow output |
| Semgrep | Community Python rules plus project-owned rules | Semgrep `ERROR` finding, project-rule test failure, or scanner error | SARIF uploaded to code scanning and retained as an artifact |
| Trivy dependency SCA | Python dependency manifests and known vulnerability data; PR/push plus recurring weekly evaluation | Fixed HIGH/CRITICAL library vulnerability or scanner failure | Full JSON report |
| Trivy container scan | Built runtime image and known vulnerability data; PR/push plus recurring weekly evaluation | Fixed HIGH/CRITICAL image vulnerability, runtime package-manager regression, or scanner failure | Full JSON and SARIF reports |
| Checkov Kubernetes IaC | Kubernetes deployment manifests and runtime-security policy | Any Checkov failure, scanner/install verification failure, or failure of the privileged-container control test | JSON report; current manifests pass without policy skips |
| OWASP ZAP Baseline | Running local SecureFlow documentation/API surface | A rule classified `FAIL` in `.zap/rules.tsv`, target startup failure, or scanner failure | Baseline report; WARN/INFO findings remain visible |
| Release image security | Release build, CycloneDX SBOM generation, immutable publication and attestations | Broken image build/SBOM validation; invalid release tag; publish or attestation failure | Validation SBOM plus release SBOM, metadata and GitHub attestations |

## IaC policy

The Kubernetes Checkov workflow is blocking after the initial observation/remediation cycle.

The initial scan found three configuration issues:

- `CKV_K8S_15` — image pull policy was not `Always`;
- `CKV_K8S_35` — JWT signing material was referenced through an environment-variable secret source;
- `CKV_K8S_43` — the application image was not pinned by digest.

The first two findings were remediated immediately. `CKV_K8S_43` was temporarily and narrowly skipped because no real SecureFlow image digest existed yet; inventing a placeholder digest would have created a false security claim.

Release `v0.1.0` subsequently published a real image and recorded the registry-provided digest:

```text
ghcr.io/simplyy-shadin/secureflow-devsecops@sha256:93a26b7b9d665574026e9dd850a75670363f97dfacda4c736babc307ab80d32c
```

The Kubernetes Deployment now uses that immutable reference and the temporary `CKV_K8S_43` exception has been removed. The current Checkov gate therefore runs with no committed policy skip for the application image.

Checkov itself is version-pinned and its downloaded release archive is checksum-verified before execution. A temporary privileged Pod is used as a negative control to verify that the policy engine rejects `CKV_K8S_16`.

## DAST policy

The ZAP workflow scans an ephemeral target created inside the GitHub Actions runner. It does not scan an external host.

The policy file uses three explicit states:

- `FAIL` for response controls that SecureFlow expects to enforce and therefore treats as regressions.
- `WARN` for residual development-surface findings that are visible but accepted with a documented reason.
- `INFO` for scanner observations that do not represent an actionable vulnerability in the current context.

The workflow uses ZAP's warning-tolerant mode so documented `WARN` findings do not make the job fail, while rules promoted to `FAIL` still block the workflow.

Current blocking DAST rules cover:

- anti-clickjacking protection;
- `X-Content-Type-Options`;
- Content Security Policy presence;
- Permissions Policy presence.

The current warning set is limited to behavior associated with the generated FastAPI Swagger UI and browser-isolation choices. Details and the before/after scan are in [dast-remediation.md](dast-remediation.md).

## Release gate

Pull requests that affect the release image build the candidate image and validate a CycloneDX SBOM without receiving package-write or signing permissions.

A version-tag event must use `vMAJOR.MINOR.PATCH`. Only the tag-triggered publish job receives the permissions needed to push to GHCR and create OIDC-backed GitHub attestations.

For `v0.1.0`, the release workflow:

1. published the image to GHCR;
2. captured the registry SHA-256 digest;
3. generated the SBOM against that published digest;
4. created signed build-provenance and SBOM attestations;
5. retained release metadata and SBOM evidence.

See [release-security.md](release-security.md) for verification commands and the exact first-release evidence.

## Finding response

When a blocking finding appears:

1. preserve enough evidence to identify the scanner, rule, affected component and commit;
2. determine whether the issue is a real defect, a scanner/configuration error, or a context-dependent risk;
3. fix the defect when practical and add a regression test or rule where appropriate;
4. rerun the same control and verify the finding is removed or intentionally reclassified;
5. document any accepted residual risk rather than deleting or globally suppressing the rule.

A real credential requires revocation or rotation even if it is later removed from Git. A vulnerable dependency should be upgraded when a fixed version is available; simply suppressing the advisory is not treated as remediation.

## Evidence retention

- Semgrep: SARIF uploaded to GitHub code scanning and retained as a workflow artifact.
- Trivy: dependency JSON plus container JSON/SARIF artifacts.
- Checkov: Kubernetes JSON report retained as a workflow artifact.
- ZAP: baseline report artifact from the ZAP action.
- Release: validation SBOM plus published-image SBOM and release metadata; attestations remain associated with the repository/registry.
- CI/Gitleaks: workflow logs provide execution evidence; secret values are redacted and not intentionally retained.

## Scope limitation

These workflows define how SecureFlow evaluates pull-request and main-branch changes. Whether every workflow is configured as a required GitHub branch-protection check is a repository setting outside the versioned workflow files, so this document does not claim that branch protection itself is enabled.
