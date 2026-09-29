# Supply-chain and container vulnerability scanning

SecureFlow treats dependency risk and container-image risk as separate controls from source-code analysis.

## Pull-request dependency review

Pull requests run GitHub's dependency review action against the dependency changes introduced by the branch.

The gate fails when a newly introduced dependency is associated with a vulnerability rated **HIGH** or **CRITICAL**.

License policy is intentionally not part of this milestone. The control is focused on known-vulnerability risk rather than mixing security and legal-policy decisions into one gate.

## Current dependency scan

Trivy also scans the repository filesystem for dependency vulnerabilities on pull requests and pushes to `main`.

The workflow creates a JSON report containing findings across all severities. A second pass acts as the blocking gate.

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

## Tool pinning

The workflow pins:

- `actions/dependency-review-action` to the commit for v5.0.0
- `aquasecurity/trivy-action` to the commit behind signed tag v0.36.0
- Trivy itself to v0.70.0
- GitHub-maintained upload actions to immutable commit SHAs

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
