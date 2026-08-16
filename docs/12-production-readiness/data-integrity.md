# Data Integrity & Zero Fake Data Policy

## 1. Zero Fake Data Guarantee
- **No Seed Records**: Production database initialization does not create synthetic complaints, fake authority users, or hardcoded analytics metrics.
- **Data Sufficiency Enforcement**:
  - The predictive intelligence engine requires a minimum of 5 historical complaints (`predictive_min_historical_complaints`). If fewer exist, it explicitly returns status `INSUFFICIENT_DATA` rather than generating artificial forecasts.
- **Server-Derived Attributes**:
  - `user_id`: Extracted from authenticated Redis session.
  - `status`: Server-controlled state transitions (`SUBMITTED` → `ASSIGNED` → `IN_PROGRESS` → `RESOLVED` → `CLOSED`).
  - `created_at`: Server-generated UTC timestamp.
  - `priority_score`: Calculated via deterministic priority scoring algorithm.

## 2. Immutable Audit Trail
- All operational authority actions (status updates, department assignments, reassignments) write append-only records to `authority_audit_trail`.
- Audit logs contain `complaint_id`, `actor_id`, `action_type`, `previous_status`, `new_status`, `note`, and `created_at`. Audit records are read-only and immutable.
