# Reliability & Resilience Audit

## 1. System Resilience & Failure Isolation
- **Database Connection Failure**: Health check endpoints report `/health/readiness` as `unhealthy` if MongoDB or Redis fails to connect during startup.
- **AI Processing Isolation**:
  - LLM failures (e.g., API key missing, network timeout, rate limit) transition AI processing status to `FAILED` and log the exception.
  - An AI processing failure does **not** corrupt or delete the citizen complaint record.
- **Notification Failure Isolation**:
  - Notification dispatch errors are caught, logged, and isolated. Status updates and complaint submissions succeed even if email/push delivery fails.
- **External Integration Isolation**:
  - If a downstream municipal government API is unconfigured, the adapter returns status `NOT_CONFIGURED` without failing the internal authority workflow.

## 2. Idempotency & Duplicate Protection
- Event processing checks for duplicate domain event execution using deterministic idempotency keys (`event_type + complaint_id + state`).
- Duplicate event execution attempts update existing records rather than creating duplicate notifications or audit entries.
