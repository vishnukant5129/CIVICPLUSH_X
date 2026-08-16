# CivicPulse AI — Authentication & Authorization

## Overview

Phase 3 establishes the security foundation for CivicPulse AI, implementing robust authentication, session management, identity verification, and role-based authorization.

## Authentication Architecture

We use a **Secure Cookie-Based Session** architecture backed by **Redis**.

- **Why chosen:** Better security for browser SPAs than localStorage JWTs. It completely eliminates XSS token theft via HttpOnly cookies and inherently supports immediate server-side revocation (logout/ban) unlike stateless JWTs. We leverage the existing Redis infrastructure from Phase 1.
- **Passwords:** Hashed securely using `passlib` with `bcrypt`. Hashes are never returned through APIs or logged.
- **Session Tokens:** 32-byte secure random strings (URL safe).
- **Cookie Settings:** `HttpOnly=True`, `Secure=True` (in production), `SameSite=Lax`.

## Authorization Model

Authorization is enforced exclusively server-side via FastAPI dependencies:
- `require_authenticated_user`
- `RoleChecker([UserRole.CITIZEN, UserRole.AUTHORITY, UserRole.ADMIN])`

The frontend receives a safe representation of the user (`UserResponse`) but has no power to elevate privileges by modifying client-side state.

## Quick Links

- [Authentication Architecture](./authentication-architecture.md)
- [Authorization Model](./authorization-model.md)
- [API Contract](./api-contract.md)
- [Testing Strategy](./testing.md)
