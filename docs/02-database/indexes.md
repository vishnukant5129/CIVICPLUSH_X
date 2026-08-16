# CivicPulse AI — Index Strategy

## Principles

1. Every index has a documented purpose and query pattern.
2. Indexes are created idempotently at application startup.
3. No manual index creation required.
4. Unique constraints enforce data integrity at DB level.

## Index Inventory

### users

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_users_normalized_email_unique` | `normalized_email` ASC | ✅ | Email uniqueness (case-insensitive via normalized field) |
| `idx_users_role` | `role` ASC | — | Filter users by role |
| `idx_users_status` | `status` ASC | — | Filter active/inactive users |

### departments

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_departments_code_unique` | `code` ASC | ✅ | Department code uniqueness for routing |
| `idx_departments_status` | `status` ASC | — | Filter active departments |

### complaints

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_complaints_user_id` | `user_id` ASC | — | "My complaints" queries |
| `idx_complaints_status` | `status` ASC | — | Filter by lifecycle status |
| `idx_complaints_category` | `category` ASC | — | Filter by civic category |
| `idx_complaints_created_at_desc` | `created_at` DESC | — | Chronological listing |
| `idx_complaints_location_geo_2dsphere` | `location.geo` 2dsphere | — | Geospatial queries ($near, $geoWithin) |
| `idx_complaints_status_priority_created` | `status` ASC + `priority_score` DESC + `created_at` DESC | — | Authority dashboard queue (filter status, sort by priority then recency) |
| `idx_complaints_cluster_id` | `cluster_id` ASC | — | Cluster membership queries |
| `idx_complaints_department_id` | `department_id` ASC | — | Department-specific queries |

### evidence

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_evidence_complaint_id` | `complaint_id` ASC | — | Fetch evidence for complaint |

### ai_analyses

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_ai_analyses_complaint_id` | `complaint_id` ASC | — | Fetch analyses for complaint |
| `idx_ai_analyses_complaint_created_desc` | `complaint_id` ASC + `created_at` DESC | — | Get latest analysis |

### incident_clusters

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_incident_clusters_category` | `category` ASC | — | Filter clusters by type |
| `idx_incident_clusters_location_2dsphere` | `representative_location` 2dsphere | — (sparse) | Geospatial cluster queries |

### assignments

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_assignments_complaint_id` | `complaint_id` ASC | — | Assignment history for complaint |
| `idx_assignments_department_id` | `department_id` ASC | — | Department workload |

### status_history

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_status_history_complaint_created` | `complaint_id` ASC + `created_at` ASC | — | Chronological timeline |

### notifications

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_notifications_recipient_created_desc` | `recipient_id` ASC + `created_at` DESC | — | User notification feed |
| `idx_notifications_recipient_status` | `recipient_id` ASC + `status` ASC | — | Unread count queries |

### predictions

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_predictions_type_status` | `prediction_type` ASC + `status` ASC | — | Active prediction queries |
| `idx_predictions_generated_at_desc` | `generated_at` DESC | — | Chronological listing |

### audit_logs

| Index | Fields | Unique | Purpose |
|-------|--------|--------|---------|
| `idx_audit_logs_resource` | `resource_type` ASC + `resource_id` ASC | — | Resource-specific audit trail |
| `idx_audit_logs_created_at_desc` | `created_at` DESC | — | Chronological queries |
| `idx_audit_logs_actor_id` | `actor_id` ASC | — | Actor-specific queries |

## Initialization

Indexes are created by `app.database.init_db.ensure_indexes()` during application startup.

- **Idempotent:** `create_index` is a no-op for existing indexes.
- **Safe:** Running startup multiple times will not fail or create duplicates.
- **Automatic:** No manual `createIndex` commands needed.

## Future Considerations

- **Vector search index:** Will be needed for semantic duplicate detection (intelligence phases).
- **Text indexes:** May be useful for complaint search (complaint phase).
- **TTL indexes:** May be useful for notifications/predictions with expiry.
