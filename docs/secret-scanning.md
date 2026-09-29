# Secret scanning

SecureFlow uses Gitleaks in CI to detect likely hardcoded credentials before changes reach `main`.

## Scanner installation

The workflow installs Gitleaks 8.30.1 from the upstream release archive. The Linux x64 archive is pinned to its published SHA-256 checksum before extraction.

The workflow does not use a floating `latest` scanner version.

## Detection control

A security gate is useful only if there is evidence that it actually blocks the condition it is meant to detect.

The workflow therefore creates a randomly generated, GitHub-PAT-shaped fake value in `$RUNNER_TEMP` and scans that temporary directory. Gitleaks must return the configured finding exit code. If it does not, the job fails.

The control value:

- is generated only on the ephemeral CI runner
- is not a real credential
- is never committed to the repository
- is redacted from Gitleaks output
- is removed before the repository scan

During implementation, an earlier CI run intentionally placed the generated control file in the working tree. The Gitleaks job failed as expected, demonstrating that the gate blocks detected credentials.

## Repository scan

After the control succeeds, Gitleaks scans Git history with the built-in rule set extended by `.gitleaks.toml`.

Checkout uses full history and the scan passes `--all` to Git so reachable repository refs are inspected rather than only the latest file snapshot.

Secrets are redacted in workflow output.

## Initial findings and remediation

The first verbose control run reported seven findings:

- one runtime-generated fake GitHub PAT used to prove the gate
- six matches of the same synthetic password literal in test files

The test password was never a real credential. Current tests now construct the value from harmless fragments at runtime so the literal is no longer present in the working tree.

Because the exact synthetic value already exists in merged Git history, rewriting published history solely to remove a non-secret test fixture would add risk without improving credential security. A narrow historical exception is therefore kept in `.gitleaks.toml`.

That exception is constrained to:

- the `generic-api-key` rule
- the exact historical synthetic value
- only the three test files where it appeared

It does not allowlist the entire `tests/` directory or disable the generic secret rule.

## Finding response policy

A Gitleaks finding is treated as a security event until reviewed.

For a real credential:

1. Revoke or rotate the credential first.
2. Remove the secret from source and replace it with environment or secret-manager configuration.
3. Review logs and access history when the credential could have been used.
4. Decide whether Git history must be rewritten based on exposure and repository distribution.
5. Re-run Gitleaks and document the remediation in the pull request.

Deleting a secret from the latest commit is not sufficient if the credential remains valid or is still present in history.

For a false positive:

1. Confirm that the value has no authentication or authorization capability.
2. Prefer changing the test/example data so it no longer resembles a credential.
3. If historical findings remain, use the narrowest practical exception: exact value, rule, and path.
4. Document why the exception exists.
5. Never add a broad allowlist only to make CI pass.

## Limitations

Gitleaks detects patterns and entropy associated with secrets. A passing scan does not prove that a repository contains no sensitive data. Code review, secret-management practices, provider-side secret scanning, and credential rotation procedures remain necessary controls.
