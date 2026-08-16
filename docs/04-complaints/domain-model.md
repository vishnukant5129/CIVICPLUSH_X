# Complaint Domain Model

## Core Models

### Complaint (`ComplaintDocument`)
The central entity for civic issues.
- `user_id` (String): **SERVER CONTROLLED.** Derived from the authenticated session. The authoritative owner.
- `title` (String): **CLIENT CONTROLLED.** Brief summary.
- `description` (String): **CLIENT CONTROLLED.** Detailed text.
- `category` (CivicCategory Enum): **CLIENT CONTROLLED.** e.g., `pothole_road_damage`.
- `location` (LocationData): **CLIENT CONTROLLED.** Address and strict GeoJSON Point for geospatial queries.
- `status` (ComplaintStatus Enum): **SERVER CONTROLLED.** Initially `SUBMITTED`. Citizens cannot modify.
- `priority_score`, `department_id`, `cluster_id`, `ai_analysis_id`: **SERVER CONTROLLED.** Null during Phase 4 (reserved for AI/Authority phases).
- `evidence_count` (Integer): **SERVER CONTROLLED.** Initially 0.
- `created_at`, `updated_at` (Datetime): **SERVER CONTROLLED.**

### StatusHistory (`StatusHistoryDocument`)
Append-only log of lifecycle transitions.
- `complaint_id` (String): **SERVER CONTROLLED.** 
- `previous_status` (ComplaintStatus): **SERVER CONTROLLED.**
- `new_status` (ComplaintStatus): **SERVER CONTROLLED.**
- `actor_id` (String): **SERVER CONTROLLED.** User who triggered the change.
- `reason` (String): Optional context.
- `created_at` (Datetime): **SERVER CONTROLLED.**
