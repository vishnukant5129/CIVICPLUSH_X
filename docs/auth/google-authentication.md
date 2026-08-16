# CivicPulse AI — Google Authentication

## Architecture

CivicPulse uses **Google OAuth 2.0 Authorization Code flow** for primary authentication.

```
Browser                    Backend                      Google
  │                           │                            │
  │── Click "Continue with    │                            │
  │   Google" ──────────────► │ GET /auth/google/start     │
  │                           │ Generate random state      │
  │                           │ Store state in Redis       │
  │◄── 302 Redirect ──────────│ ──────────────────────────►│
  │                           │                            │ Google
  │                           │                            │ Sign-In
  │◄──────────────────────────────────────────────────────►│ Page
  │                           │                            │
  │                           │◄── 302 callback ───────────│
  │                           │    ?code=...&state=...     │
  │                           │                            │
  │                           │ 1. Validate state (CSRF)   │
  │                           │ 2. Exchange code→ tokens   │
  │                           │ 3. Verify ID token         │
  │                           │    (signature+aud+iss+exp) │
  │                           │ 4. Find/Create user        │
  │                           │ 5. Create Redis session    │
  │                           │ 6. Set HttpOnly cookie     │
  │◄── 302 / (+ cookie) ──────│                            │
  │                           │                            │
  │── GET /api/v1/auth/me ───►│ Read session from Redis    │
  │◄── UserResponse ──────────│                            │
```

**Google passwords are entered ONLY on Google's domain. CivicPulse never sees them.**

---

## Security Model

| Property | Value |
|---|---|
| Session type | Opaque random token (32 bytes) |
| Session storage | Redis (`session:<token>` key) |
| Session TTL | 7 days, rolling |
| Cookie name | `civicpulse_session` |
| Cookie flags | `HttpOnly`, `SameSite=Lax`, `Secure` in production |
| State token TTL | 10 minutes, single-use |
| ID token verification | Via `google-auth` library (signature + audience + issuer + expiry) |
| `google_sub` | Stable, immutable Google user identity key |
| Google tokens stored | **Never** (access/refresh tokens are not persisted) |
| Client secret location | Backend only (never in browser, never in VITE_* vars) |
| New account role | Always `CITIZEN` |

---

## Required Environment Variables

### Backend (`.env` / Docker environment)

| Variable | Description | Example |
|---|---|---|
| `GOOGLE_CLIENT_ID` | OAuth 2.0 Client ID (public) | `1234-xxx.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 Client Secret (**secret**) | `GOCSPX-...` |
| `GOOGLE_REDIRECT_URI` | Callback URI (must match Google Cloud) | `http://localhost:8000/api/v1/auth/google/callback` |

### Frontend (Vite env)

| Variable | Description |
|---|---|
| `VITE_GOOGLE_CLIENT_ID` | Same Client ID as backend — safe for browser |

> **GOOGLE_CLIENT_SECRET is NEVER set in VITE_ variables.**

---

## Google Cloud Setup

### Step 1 — Create a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Name it `CivicPulse` (or any name)
4. Click **Create**

### Step 2 — Configure OAuth Consent Screen

1. Navigate to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (for any Google account users)
3. Fill in:
   - **App name**: `CivicPulse AI`
   - **User support email**: your Gmail address
   - **Developer contact information**: your email
4. Click **Save and Continue**
5. On **Scopes** page: click **Add or Remove Scopes**
   - Add: `openid`, `email`, `profile`
6. Click **Save and Continue** through the rest
7. On **Test users**: add `arbab2171217@gmail.com` during development
8. Submit

> **While the app is in "Testing" status, only test users can sign in.**
> To allow all Google accounts, submit for verification.

### Step 3 — Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `CivicPulse Web`
5. **Authorized JavaScript origins** (for development):
   ```
   http://localhost:5173
   http://localhost:8000
   ```
6. **Authorized redirect URIs** (exact match required):
   ```
   http://localhost:8000/api/v1/auth/google/callback
   ```
7. Click **Create**
8. Copy the **Client ID** and **Client Secret**

### Step 4 — Configure `.env`

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

> Do NOT commit `.env` to Git. It is already in `.gitignore`.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/auth/google/start` | Redirect to Google authorization |
| `GET` | `/api/v1/auth/google/callback` | Handle Google callback, create session |
| `GET` | `/api/v1/auth/me` | Get current authenticated user |
| `POST` | `/api/v1/auth/logout` | Destroy Redis session + clear cookie |

---

## User Creation & Account Linking

When a user authenticates with Google for the first time:

1. Backend verifies the ID token (cryptographic signature + claims).
2. Looks up user by `google_sub` (stable Google user ID).
3. If not found by `sub`, checks for existing account with same verified email.
4. If an email match exists → links `google_sub` to the existing account.
5. If no existing account → creates a new `CITIZEN` account.
6. Role is **always forced to `CITIZEN`** for public sign-in.
7. Creates a CivicPulse Redis session.
8. Sets `civicpulse_session` HttpOnly cookie.
9. Redirects to frontend `/`.

---

## Database Schema (MongoDB `users` collection)

New fields added for Google OAuth support:

```json
{
  "_id": "ObjectId",
  "email": "user@gmail.com",
  "normalized_email": "user@gmail.com",
  "display_name": "User's Name",
  "google_sub": "1234567890",
  "profile_picture_url": "https://lh3.googleusercontent.com/...",
  "role": "citizen",
  "status": "active",
  "password_hash": null,
  "created_at": "2026-08-16T...",
  "updated_at": "2026-08-16T..."
}
```

**Indexes:**
- `normalized_email` — unique, required
- `google_sub` — unique, sparse (only indexed when present)

---

## Error Codes (Frontend Redirect Parameters)

When authentication fails, the backend redirects to `/?auth_error=<code>`:

| Code | Meaning |
|---|---|
| `cancelled` | User cancelled at Google |
| `google_error` | Google returned an error |
| `state_mismatch` | CSRF state validation failed |
| `missing_code` | Authorization code was absent |
| `token_exchange_failed` | Code exchange with Google failed |
| `identity_verification_failed` | ID token could not be verified |
| `duplicate_account` | Email conflict during account creation |
| `account_disabled` | CivicPulse account is disabled |
| `service_unavailable` | Database/Redis unavailable |

---

## Production Setup

For production deployment, update:

**Authorized redirect URIs** in Google Cloud Console:
```
https://api.yourcivicpulse.com/api/v1/auth/google/callback
```

**Backend `.env`:**
```env
GOOGLE_REDIRECT_URI=https://api.yourcivicpulse.com/api/v1/auth/google/callback
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

The `Secure` flag on the session cookie is automatically enabled when `APP_ENV=production`.

---

## What is NOT Implemented

- **Email OTP**: Not implemented. If needed in future, requires a real email provider (SendGrid, AWS SES, etc.).
- **Google password receipt**: CivicPulse never receives, stores, or processes Google passwords.
- **Refresh token storage**: Not stored anywhere. Sessions are managed by CivicPulse Redis, not Google tokens.
- **Gemini API confusion**: `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` are OAuth credentials. `GEMINI_API_KEY` is a separate AI API key from Google AI Studio. They are different systems.
