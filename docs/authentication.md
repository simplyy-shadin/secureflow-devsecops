# Authentication design

SecureFlow uses short-lived JWT access tokens for the current authentication milestone. The implementation is deliberately small enough to review while still making the security decisions explicit.

## Registration

`POST /auth/register` validates and normalizes the email address, hashes the password with Argon2id, stores only the resulting password hash, and returns a response model that excludes password material.

Duplicate normalized email addresses return `409 Conflict`.

## Login

`POST /auth/login` accepts an email address and password and returns a Bearer access token when the credentials are valid.

Unknown accounts and incorrect passwords return the same `401 Unauthorized` response. When the account does not exist, SecureFlow still performs an Argon2 verification against a dummy hash. This reduces the obvious timing difference between "unknown account" and "wrong password" paths, but it should not be treated as a complete side-channel defense.

## Access tokens

Access tokens are signed with HS256. The accepted algorithm is fixed in code rather than read from the token header.

The token includes and validates:

- `sub`: numeric user identifier encoded as a string
- `iss`: configured issuer
- `aud`: configured audience
- `iat`: issued-at time
- `exp`: expiration time

The default access-token lifetime is 15 minutes and is configurable between 5 and 60 minutes.

`GET /users/me` requires a valid Bearer token and loads the referenced user from the database. A token for a user that no longer exists is rejected.

## Signing-key handling

The JWT signing key has no repository default. `JWT_SECRET_KEY` must be supplied through the environment and must contain at least 32 characters.

For local development, generate a value with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Store that value only in the ignored local `.env` file.

GitHub Actions generates a new ephemeral signing key at runtime for the container smoke test. No CI signing key is committed to the repository.

## Current boundaries

This milestone intentionally does not add refresh tokens, token revocation, multi-factor authentication, roles, permissions, or account lockout. Those are separate concerns and should be introduced only when the application has a requirement for them.

Rate limiting is also not implemented yet. Before exposing the login endpoint to an untrusted public network, rate limiting and abuse monitoring would be expected controls.

SQLite and startup-time table creation remain development conveniences. They are documented separately and are not presented as a production database or migration strategy.
