# Contributing

SecureFlow is maintained as an issue-driven security engineering project. Changes should be small enough to review and should explain the security or engineering reason behind them.

## Workflow

1. Start from an existing issue or create one that describes the problem.
2. Create a focused branch from `main`.
3. Keep commits scoped and descriptive.
4. Open a pull request that explains what changed, why it changed, and how it was tested.
5. Resolve review feedback and CI failures before merge.

## Branch names

Use short names that describe the change:

- `feat/api-foundation`
- `chore/project-foundation`
- `security/gitleaks`
- `security/semgrep`
- `fix/remove-hardcoded-secret`

## Commit messages

Use an action-oriented prefix where it helps the history stay readable:

- `feat:` application behavior
- `fix:` bug or vulnerability remediation
- `security:` security controls and detections
- `ci:` workflow changes
- `docs:` documentation
- `chore:` repository maintenance

Examples:

`security: integrate Gitleaks secret scanning`

`fix: remove hardcoded signing key`

`docs: document threat model trust boundaries`

## Security test cases

Deliberately vulnerable examples must:

- use fake data only
- be isolated from real services
- state what control they are validating
- be removed or remediated as part of the documented exercise

Do not commit real secrets or credentials, even temporarily.
