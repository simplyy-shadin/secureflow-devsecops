# Security Policy

SecureFlow is an educational security engineering project. Some branches and pull requests may contain deliberately vulnerable code used to validate security controls.

## Reporting a vulnerability

If you find an issue that is not part of a documented test case, please avoid publishing exploit details in a public issue.

Open a GitHub security advisory when private vulnerability reporting is available for this repository. If that option is unavailable, contact the repository owner directly through the contact information on the GitHub profile.

Please include:

- the affected file or component
- a concise description of the issue
- steps required to reproduce it
- expected security impact
- any suggested remediation, if known

## Scope

Reports about the SecureFlow codebase and its CI/CD configuration are in scope.

The intentionally vulnerable third-party applications or test fixtures used by this project are governed by their own security policies.

## Test data

Only fake credentials, synthetic data, and local test targets should be used in this repository. Real API keys, access tokens, passwords, or personal data must not be committed.
