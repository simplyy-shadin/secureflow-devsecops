# Security gate model

SecureFlow uses several independent checks rather than treating one scanner as proof that the application is secure. Each workflow has a defined blocking threshold so a finding is not made non-blocking simply to obtain a green build.

## Gate semantics

- **PASS** — the control completed successfully and no finding met its blocking threshold.
- **WARN / observation** — the control produced a finding that remains visible but is not currently a merge blocker. The rationale must be documented and revisited if the affected surface changes.
- **FAIL** — the workflow or scanner failed, or a finding met the control's blocking threshold.

A non-blocking result is not the same as a fixed vulnerability. Reports are retained where useful so lower-severity or contextual findings remain reviewable.

## Current gates

| Control | What it validates | Blocking condition | Non-blocking evidence |
| --- | --- | --- | --- |
| CI | Ruff, pytest, container runtime behavior, registration/login/profile flow, restart persistence | Lint/test failure, container startup failure, runtime-hardening regression, or failed smoke assertion | None; these checks are binary |
| Gitleaks | Current repository and Git history | Any detected credential/secret, scanner failure, or failure of the generated fake-secret self-test | Redacted scanner output; secrets are not retained as artifacts |
| Semgrep | Community Python rules plus project-owned rules | Semgrep `ERROR` finding, project-rule test failure, or scanner error | SARIF is uploaded to code scanning and retained as an artifact |
| Trivy dependency SCA | Python dependency manifests and known vulnerability data | Fixed HIGH/CRITICAL library vulnerability or scanner failure | Full JSON report includes lower severities and unfixed findings |
| Trivy container scan | Built runtime image and known vulnerability data | Fixed HIGH/CRITICAL image vulnerability, runtime package-manager regression, or scanner failure | Full JSON and SARIF reports are retained |
| OWASP ZAP Baseline | Running local SecureFlow HTTP surface | A rule classified `FAIL` in `.zap/rules.tsv`, target startup failure, or scanner failure | Rules classified `WARN` stay visible; `INFO` is retained as scanner context |

## DAST policy

The ZAP workflow scans an ephemeral target created inside the GitHub Actions runner. It does not scan an external host.

The policy file uses three explicit states:

- `FAIL` for response controls that SecureFlow expects to enforce and therefore treats as regressions.
- `WARN` for residual development-surface findings that are visible but accepted with a documented reason.
- `INFO` for scanner observations that do not represent an actionable vulnerability in the current context.

The workflow uses ZAP's warning-tolerant mode so documented `WARN` findings do not make the job fail, while rules promoted to `FAIL` still block the workflow.

Current blocking DAST rules cover:

- anti-clickjacking protection
- `X-Content-Type-Options`
- Content Security Policy presence
- Permissions Policy presence

The current warning set is limited to behavior associated with the generated FastAPI Swagger UI and browser isolation choices. Details and the before/after scan are in [dast-remediation.md](dast-remediation.md).

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
- ZAP: baseline report artifact from the ZAP action.
- CI/Gitleaks: workflow logs provide execution evidence; secret values are redacted and not intentionally retained.

## Scope limitation

These workflows define how SecureFlow evaluates pull-request and main-branch changes. Whether every workflow is configured as a required GitHub branch-protection check is a repository setting outside the versioned workflow files, so this document does not claim that branch protection itself is enabled.
