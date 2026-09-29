# Supply-chain and container vulnerability scanning

SecureFlow treats dependency risk and container-image risk as separate controls from source-code analysis.

## Pull-request dependency review

Every pull request checks out full Git history and prints changes to `requirements.txt` and `requirements-dev.txt` before scanning the resulting dependency set.

The first implementation attempted GitHub's dependency review action. The action failed because Dependency Graph is not enabled for this repository. Rather than make an account-level repository setting a hidden prerequisite for the security gate, SecureFlow uses a portable Trivy filesystem SCA scan on every pull request and push to `main`.

This means dependency changes are visible in CI and the complete resulting manifest set is scanned for published vulnerabilities.

## Current dependency scan

The supply-chain workflow runs on pull requests, pushes to `main`, a weekly schedule, and manual dispatch. The scheduled run matters because vulnerability knowledge can change even when the repository does not: a newly published CVE should not wait for the next source-code commit before the pinned dependency and container state is re-evaluated.

Trivy creates a JSON report containing findings across all severities. A second pass acts as the blocking gate.

Blocking policy:

- severity: HIGH or CRITICAL
- a fix must currently be available
- fixed actionable findings fail CI

Unfixed HIGH or CRITICAL findings remain visible in the report but do not automatically fail the build. They still require review because lack of an upstream fix does not make the vulnerability harmless.

This split keeps the gate focused on findings the project can act on immediately while retaining evidence about unresolved upstream risk.

## Container image scan

The workflow builds the same `Dockerfile` used by SecureFlow and scans the resulting local image with Trivy.

Outputs include:

- a full JSON vulnerability report across all severities
- HIGH and CRITICAL findings in SARIF for GitHub code scanning
- a blocking HIGH/CRITICAL gate for vulnerabilities with an available fix

The JSON and SARIF files are retained as short-lived workflow artifacts for review and troubleshooting.

## Initial gate findings and remediation

The first supply-chain run blocked the pull request on real actionable findings.

### PyJWT

The dependency and image scans found two HIGH vulnerabilities in `PyJWT==2.10.1`:

- CVE-2026-32597, fixed in 2.12.0
- CVE-2026-48526, fixed in 2.13.0

SecureFlow upgraded the direct dependency to `PyJWT==2.13.0` so both findings are addressed by the same reviewed version change.

### Packaging-tool findings

The image scan also reported HIGH findings for `msgpack==1.1.2` and `setuptools==70.3.0`.

A follow-up build check showed that neither package was installed as a top-level runtime package: pip reported both as absent when removal was attempted. The findings remained under Trivy's aggregate Python package target, alongside a warning that third-party SBOM data can lead to inaccurate vulnerability detection.

Both components are associated with Python packaging tooling rather than SecureFlow's runtime dependency set. SecureFlow does not need pip inside the running API container after dependencies are installed, so the final image removes pip itself after installation instead of adding ignore rules for the reported components.

CI verifies that the built runtime can no longer import pip before the image vulnerability gate runs. This reduces runtime attack surface and removes the stale packaging-tool inventory at its source rather than suppressing scanner output.

The image scan remains the validation point for that decision.

## Tool pinning

The workflow pins:

- `aquasecurity/trivy-action` to the commit behind signed tag v0.36.0
- Trivy itself to v0.70.0
- GitHub-maintained checkout, SARIF, and artifact actions to immutable commit SHAs

Pinning the action code and scanner version reduces silent changes in CI behavior. Trivy's vulnerability databases remain intentionally updateable because stale advisory data would reduce scan value.

## Exceptions

No vulnerability is ignored solely to make the pipeline pass.

If an exception becomes necessary, the pull request must document:

1. the vulnerability identifier
2. the affected component and version
3. why remediation is not currently practical
4. compensating controls or exposure constraints
5. an owner
6. a review or expiry date

Exceptions should be scoped to the smallest possible identifier and component. Broad severity exclusions, whole-directory skips, or unbounded ignore files are not acceptable.

## Limitations

Dependency and image scanners depend on published advisory data and package identification. A clean scan does not prove that a dependency is free from vulnerabilities, and a reported CVE still requires reachability and exposure review.

These controls complement source analysis, secret scanning, dynamic testing, threat modeling, and manual review rather than replacing them.
