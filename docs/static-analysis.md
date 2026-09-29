# Static application security testing

SecureFlow uses Semgrep to inspect Python source before changes are merged.

## Scan layers

The SAST job has two layers:

1. A community Python baseline from the Semgrep Registry for broad coverage.
2. Project-owned rules in `security/semgrep/secureflow.yml` for policies that are especially important to SecureFlow.

The Semgrep CLI is pinned in CI so scanner behavior does not change silently between runs.

## Project-owned rules

### `secureflow.no-shell-true`

This rule rejects common `subprocess` APIs when `shell=True` is enabled.

SecureFlow has no current requirement to invoke a shell. Treating shell execution as a prohibited pattern reduces the chance that future request data is accidentally passed into a command interpreter.

The rule is intentionally narrow: it does not claim that every subprocess call is safe. Argument construction and executable selection still require review.

### `secureflow.no-pickle-deserialization`

This rule rejects Python `pickle.load` and `pickle.loads`.

Pickle is capable of executing code during deserialization and is not an appropriate interchange format for untrusted application data. SecureFlow should use non-executable formats such as JSON for data crossing trust boundaries.

The rule is deliberately strict because the application currently has no legitimate pickle use case.

## Rule tests

The controlled vulnerable examples are stored in `security/semgrep/secureflow.py`, beside the matching rule file. They are test fixtures, not application code.

Each custom rule has:

- a `ruleid` example that must be detected
- an `ok` example representing the preferred pattern

CI runs Semgrep's rule-test mode before scanning the application. This proves that custom rules still detect their intended patterns when they are edited.

## Finding policy

High-confidence SAST findings block the SAST job. A finding should be handled by:

1. confirming the data flow and whether the issue is reachable
2. mapping the finding to the relevant code and trust boundary
3. fixing the unsafe pattern when practical
4. adding or updating a regression test
5. re-running Semgrep before merge

A finding should not be suppressed only to make CI green. Any exception must be narrow, documented, and justified in review.

## SARIF

The workflow writes Semgrep results as SARIF and uploads them to GitHub code scanning when the repository supports SARIF ingestion. The same SARIF file is retained as a short-lived workflow artifact for review and troubleshooting.

CI output remains the authoritative merge gate; SARIF is an additional review surface.

## Reproducibility

The Semgrep CLI is pinned to version 1.178.0. The community `p/python` ruleset is fetched from the Semgrep Registry, so its contents can evolve independently of the CLI version. That trade-off gives broader maintained coverage but is less reproducible than vendoring a ruleset snapshot.

Project-owned rules are versioned in this repository and tested on every pull request.

## Limitations

Semgrep is pattern and data-flow analysis, not a proof that code is secure. It can miss vulnerabilities whose behavior depends on runtime state, framework configuration, authorization design, or external services. Dynamic testing, dependency analysis, threat modeling, and manual review remain separate controls.
