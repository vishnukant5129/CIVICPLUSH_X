# CivicPulse AI — Antigravity Implementation Contract

## 1. Purpose

This document defines how Antigravity must implement CivicPulse AI.

Antigravity MUST read:
1. `MASTER_PLAN.md`
2. `docs/01-product/PRD.md`
3. `docs/01-product/MVP_SCOPE.md`
4. all applicable documents under `docs/02-system-design/`

before implementing a major feature.

## 2. Absolute Rules

### Rule 1 — No Fake Data

Never add:
- fake dashboard metrics,
- fake complaint objects,
- fake API responses,
- fake map markers,
- fake users,
- fake notifications,
- random generated values in production paths.

If a development seed is needed, create an explicit seed command/script and document it.

### Rule 2 — No Hardcoded Secrets

Never put:
- API keys,
- passwords,
- tokens,
- database URLs containing credentials

in source code.

Use environment variables/secrets.

### Rule 3 — No Hardcoded Business Data

Do not hardcode:
- departments,
- category IDs,
- user IDs,
- complaint IDs,
- geographic coordinates,
- dynamic statistics,
- provider credentials.

Configuration belongs in configuration files/environment variables; domain entities belong in the database.

### Rule 4 — Do Not Pretend Planned Features Exist

A feature is only considered implemented after:
- code exists,
- integration works,
- tests pass,
- behavior is verified.

Do not create UI labels claiming a backend feature exists when it does not.

### Rule 5 — No Silent Architecture Changes

If implementation requires changing:
- database,
- API contract,
- authentication,
- architecture,
- AI pipeline,

update the relevant documentation first and explain the reason.

### Rule 6 — Preserve Existing Working Code

Before modifying an existing module:
1. inspect it,
2. understand dependencies,
3. identify the smallest safe change,
4. avoid unnecessary rewrites.

## 3. Implementation Sequence

Antigravity should follow this order unless a documented dependency requires otherwise:

```text
1. Repository audit
2. Environment/configuration
3. Database models/repositories
4. Authentication/authorization
5. Complaint domain
6. Evidence handling
7. Complaint APIs
8. AI classification
9. Similarity/duplicate detection
10. Geo intelligence
11. Priority engine
12. Department routing
13. Authority dashboard APIs
14. Frontend citizen flow
15. Frontend authority flow
16. WebSocket/events
17. Analytics
18. Prediction
19. Testing
20. Deployment
```

## 4. Before Coding Each Phase

Create/confirm:

```text
Goal
Inputs
Outputs
Dependencies
Database changes
API changes
Frontend changes
Failure states
Tests
Acceptance criteria
```

## 5. API Rule

Never create an API only because the frontend currently needs a shortcut.

Every endpoint must have:
- purpose,
- authentication requirement,
- authorization requirement,
- request schema,
- response schema,
- error behavior.

## 6. Database Rule

Before adding a field:
- identify its owner,
- identify why it exists,
- define type/validation,
- define index requirements,
- define lifecycle.

Do not create duplicate fields representing the same concept without justification.

## 7. Frontend Rule

The frontend must fetch real state from APIs.

Never use hardcoded arrays as substitutes for backend functionality.

Loading, empty and error states are required.

## 8. AI Rule

AI outputs must pass schema validation.

Never trust raw LLM output.

AI failures must be explicit and recoverable.

## 9. Testing Rule

Every major feature requires:
- unit tests for deterministic business logic,
- integration tests for API/database workflows,
- frontend tests where behavior is complex,
- AI evaluation tests where applicable.

## 10. Completion Rule

Do not mark a task complete because code was generated.

A task is complete only when its acceptance criteria have been verified.

Use this status:

```text
PLANNED
DESIGNED
IMPLEMENTING
IMPLEMENTED
TESTING
VERIFIED
```

## 11. Final Verification

Before claiming the project is complete, verify:

- fresh environment setup,
- environment variables,
- database connection,
- authentication,
- authorization,
- complaint creation,
- evidence upload,
- AI pipeline,
- duplicate/cluster behavior,
- priority,
- dashboard,
- status transitions,
- real-time updates,
- analytics,
- error states,
- tests,
- production build.

## 12. Conflict Resolution

When two documents conflict:

1. Security rules win.
2. Product requirements win over UI assumptions.
3. Latest approved architecture decision wins.
4. Implementation shortcuts never override documented requirements.
5. If ambiguity remains, stop and surface the conflict instead of guessing.

## 13. Documentation Maintenance

After a significant implementation decision, update the corresponding `.md` document.

The documentation must describe the actual system, not an aspirational system.

## 14. Golden Principle

> Build the exact product specified by the documentation, using real data and real integrations, and never hide missing functionality behind fake UI or hardcoded values.
