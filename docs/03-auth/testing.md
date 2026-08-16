# Testing Strategy for Authentication

## Backend Testing

Backend authentication logic is strictly tested using mocked database and Redis instances, ensuring that tests run extremely fast and remain perfectly isolated.

### Test Coverage (`tests/test_auth.py`)

- **Registration (`TestRegistration`)**
  - Verify a new user receives the `CITIZEN` role.
  - Verify password hashes and sensitive secrets are completely omitted from the API response.
  - Verify a secure `HttpOnly` session cookie is successfully attached to the response.
  - Verify `409 Conflict` is correctly returned on duplicate email creation attempts.

- **Login (`TestLogin`)**
  - Verify login provides a valid cookie and returns public user data.
  - Verify incorrect passwords yield generic `401 Unauthorized` responses to prevent user enumeration.

- **Current User & Logout (`TestMeAndLogout`)**
  - Verify unauthenticated requests to protected endpoints return `401 Unauthorized`.
  - Verify `POST /logout` yields a `204 No Content` and expires the session cookie.
