# Authentication Architecture

## Mechanism: Redis-Backed Secure Sessions

### 1. Storage
- **Server:** Redis key `session:{session_id}` storing `{user_id, role, created_at}`.
- **Client:** `civicpulse_session` cookie containing the opaque `session_id`.

### 2. Cookie Security Flags
- **HttpOnly:** `True` (prevents XSS from reading the token).
- **Secure:** `True` in production (requires HTTPS), `False` in development.
- **SameSite:** `Lax` (prevents cross-site requests while allowing top-level navigation).

### 3. Session Lifecycle
- **Creation:** Upon successful `/login` or `/register`.
- **Duration:** 7 days (604800 seconds).
- **Rolling Extension:** Accessing the session resets the TTL back to 7 days.
- **Revocation/Logout:** The `/logout` endpoint immediately deletes the Redis key and clears the cookie. If an account is suspended, the database check in `get_current_user` will fail subsequent requests, effectively revoking access.

## Identity Normalization
- Emails are stripped of whitespace and converted to lowercase (`normalized_email`).
- The database enforces uniqueness on `normalized_email` via a unique index.

## Password Hashing
- **Algorithm:** `bcrypt` (via `passlib`).
- **Configuration:** Passlib's recommended secure defaults.
- **Handling:** Plaintext passwords are NEVER stored. Hashes are NEVER returned via API endpoints or logged.

## Security Controls
- **User Enumeration Prevention:** Login failures return a generic "Invalid email or password" whether the email exists, the password is wrong, or the account is disabled.
- **Privilege Escalation Prevention:** Registration strictly forces the `CITIZEN` role. `ADMIN` or `AUTHORITY` users cannot be self-created through the public API.
