# CivicPulse AI — Database Architecture

## Overview

Phase 2 establishes the MongoDB data foundation for CivicPulse AI.

All 11 domain collections are defined with validated schemas, indexed,
and accessible through a clean repository layer.

## Collections

| Collection | Purpose | Key Indexes |
|------------|---------|-------------|
| `users` | User accounts and roles | `normalized_email` (unique), `role`, `status` |
| `departments` | Civic departments | `code` (unique), `status` |
| `complaints` | Civic problem reports | `user_id`, `status`, `category`, `created_at`, `location.geo` (2dsphere), compound: `status+priority+created_at`, `cluster_id`, `department_id` |
| `evidence` | Uploaded evidence metadata | `complaint_id` |
| `ai_analyses` | AI analysis results | `complaint_id`, compound: `complaint_id+created_at` |
| `incident_clusters` | Geographic/semantic clusters | `category`, `representative_location` (2dsphere, sparse) |
| `assignments` | Department assignments | `complaint_id`, `department_id` |
| `status_history` | Complaint status transitions | compound: `complaint_id+created_at` |
| `notifications` | User notifications | compound: `recipient_id+created_at`, `recipient_id+status` |
| `predictions` | Predictive intelligence | compound: `prediction_type+status`, `generated_at` |
| `audit_logs` | Critical action audit trail | compound: `resource_type+resource_id`, `created_at`, `actor_id` |

## Quick Links

- [Schema Details](./schema.md)
- [Index Strategy](./indexes.md)
- [Data Modeling Decisions](./data-modeling-decisions.md)
- [Repository Design](./repository-design.md)
- [Testing](./testing.md)
