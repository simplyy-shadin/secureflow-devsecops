# DAST remediation case study

This case study records the first OWASP ZAP Baseline cycle for SecureFlow. The target was the local FastAPI Swagger surface running in an ephemeral container on the GitHub Actions runner.

## Baseline observation

The first observation-only scan ran against commit `a7c45ba` before response-header hardening was added.

ZAP reported:

```text
FAIL: 0
WARN: 9
INFO: 0
PASS: 58
```

The warnings included:

| ZAP rule | Observation | Useful project-level mapping |
| --- | --- | --- |
| 10020 | Missing Anti-clickjacking Header | CWE-1021; OWASP Top 10 A05: Security Misconfiguration |
| 10021 | X-Content-Type-Options Header Missing | CWE-693; OWASP A05 |
| 10038 | Content Security Policy Header Not Set | CWE-693; OWASP A05 |
| 10049 | Storable and Cacheable Content | OWASP A05, context dependent |
| 10063 | Permissions Policy Header Not Set | CWE-693; OWASP A05 |
| 10017 | Cross-Domain JavaScript Source File Inclusion | CWE-829; OWASP A08: Software and Data Integrity Failures |
| 10109 | Modern Web Application | Scanner classification rather than a vulnerability |
| 90003 | Sub Resource Integrity Attribute Missing | CWE-353; OWASP A08 |
| 90004 | Cross-Origin-Embedder-Policy Header Missing or Invalid | Browser-isolation hardening; no forced CWE mapping |

The mappings above are used to organize the findings; they do not imply that every ZAP alert is independently proof of an OWASP Top 10 vulnerability.

## Remediation

SecureFlow added application-level response-header middleware and regression tests.

The API now applies:

```text
Content-Security-Policy
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: camera=(), microphone=(), geolocation=()
Cache-Control: no-store
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
```

The API and documentation surfaces use different CSPs. The API uses a restrictive default-deny policy. The generated Swagger UI requires selected CDN/script/style allowances, so its policy is intentionally broader and documented rather than copied to all API responses.

The following ZAP checks were promoted to blocking `FAIL` rules because SecureFlow now expects those controls to remain present:

- 10020 — anti-clickjacking
- 10021 — `X-Content-Type-Options`
- 10038 — CSP header presence
- 10063 — Permissions Policy

## Verification after remediation

The gated scan after remediation reported:

```text
FAIL: 0
WARN: 4
INFO: 2
PASS: 61
```

The four remaining warnings are:

- 10017 — Swagger UI loads JavaScript from the documented jsDelivr source.
- 10055 — the Swagger UI CSP requires `unsafe-inline` for the generated development documentation surface.
- 90003 — generated Swagger UI external assets do not carry SRI attributes controlled by this application.
- 90004 — Cross-Origin-Embedder-Policy is not required for the current API/browser use case.

Two findings are classified as informational:

- 10049 — SecureFlow explicitly sends `Cache-Control: no-store`; the scanner's cacheability observation is retained for context.
- 10109 — "Modern Web Application" describes application behavior and is not treated as a vulnerability.

These findings are not globally ignored. They remain visible in the ZAP output and are tied to the current documentation surface. If Swagger delivery changes, the policy should be reviewed rather than assumed to remain valid.

## Why HSTS is not claimed

The CI target intentionally runs over local HTTP. SecureFlow therefore does not claim HSTS or production transport security as an implemented application control. TLS termination and HSTS belong at a future HTTPS deployment boundary and are listed as residual risks in the threat model.

## Result

The exercise demonstrates the full finding lifecycle:

```text
observe -> classify -> remediate -> test -> gate -> document residual risk
```

The goal was not to force ZAP to report zero warnings. The goal was to remove actionable defects, make expected controls regression-blocking, and leave contextual residual findings visible with a specific rationale.
