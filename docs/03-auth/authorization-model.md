# Authorization Model

## Philosophy
Authentication answers **"Who are you?"**
Authorization answers **"Are you allowed to do this?"**

## Roles
The system defines exactly three roles (`app.domain.enums.UserRole`):
1. `CITIZEN`: Standard public user.
2. `AUTHORITY`: Civic department worker.
3. `ADMIN`: System administrator.

## Backend Authorization Primitives
Authorization is enforced server-side using FastAPI dependencies:

### `get_current_user`
Resolves the `session_id` from the cookie, checks Redis, and retrieves the active user from the database. Returns `None` if unauthenticated or suspended.

### `require_authenticated_user`
Depends on `get_current_user` and strictly requires a valid session. Returns `401 Unauthorized` if invalid.

### `RoleChecker(allowed_roles: List[UserRole])`
A dependency generator that asserts the authenticated user has one of the required roles. Returns `403 Forbidden` if denied.

## Frontend Authorization
The frontend manages routing based on the authenticated context but **does not enforce security**.
- Protected routes redirect unauthenticated users.
- Role-restricted routes show "Access Denied" or redirect unauthorized roles.
- Actual data security relies entirely on backend validation.
