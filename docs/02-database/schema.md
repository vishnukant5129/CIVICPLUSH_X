# CivicPulse AI — Database Schema

## Conventions

- **Timestamps:** UTC, using `created_at` / `updated_at` fields.
- **IDs:** MongoDB ObjectId (`_id`). Serialized to string `id` for API consumers.
- **Naming:** All collection names are lowercase snake_case.
- **Enums:** Stored as lowercase string values, validated by Pydantic schemas.

---

## users

**Purpose:** User accounts and identity.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `email` | string | ✅ | max 254, contains `@` | User email |
| `normalized_email` | string | ✅ | lowercase, max 254 | Lowercased email for unique index |
| `display_name` | string | ✅ | min 1, max 100 | Display name |
| `role` | string | ✅ | enum: citizen, authority, admin | User role |
| `department_id` | string | — | — | Department reference (authority only) |
| `status` | string | ✅ | enum: active, inactive, suspended | Account status |
| `created_at` | datetime | ✅ | UTC | Creation timestamp |
| `updated_at` | datetime | ✅ | UTC | Last update timestamp |

**Note:** No password field in Phase 2. Authentication mechanism decided in Phase 3.

---

## departments

**Purpose:** Civic departments (database-backed, not hardcoded).

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `name` | string | ✅ | min 1, max 200 | Department name |
| `code` | string | ✅ | min 1, max 50 | Unique department code |
| `description` | string | — | max 1000 | Description |
| `status` | string | ✅ | enum: active, inactive | Operational status |
| `created_at` | datetime | ✅ | UTC | Creation timestamp |
| `updated_at` | datetime | ✅ | UTC | Last update timestamp |

---

## complaints

**Purpose:** Citizen civic problem reports. Central domain object.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `user_id` | string | ✅ | — | Reference to submitting user |
| `title` | string | ✅ | min 5, max 300 | Complaint title |
| `description` | string | ✅ | min 10, max 5000 | Detailed description |
| `category` | string | ✅ | enum: CivicCategory | Civic problem category |
| `location` | embedded | ✅ | LocationData | Location with GeoJSON point |
| `location.geo` | GeoJSON Point | ✅ | coordinates validated | `[longitude, latitude]` |
| `location.address` | string | — | max 500 | Human-readable address |
| `location.locality` | string | — | max 200 | Locality name |
| `location.city` | string | — | max 100 | City |
| `location.pincode` | string | — | max 20 | Postal code |
| `status` | string | ✅ | enum: ComplaintStatus | Lifecycle status |
| `priority_score` | float | — | 0-100 | Computed priority |
| `department_id` | string | — | — | Assigned department |
| `cluster_id` | string | — | — | Incident cluster reference |
| `ai_analysis_id` | string | — | — | Latest AI analysis reference |
| `evidence_count` | int | ✅ | ≥0, default 0 | Denormalized evidence count |
| `created_at` | datetime | ✅ | UTC | Submission timestamp |
| `updated_at` | datetime | ✅ | UTC | Last update timestamp |

---

## evidence

**Purpose:** Uploaded evidence metadata.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `complaint_id` | string | ✅ | — | Parent complaint |
| `user_id` | string | ✅ | — | Uploading user |
| `storage_key` | string | ✅ | max 500 | Storage reference key |
| `original_filename` | string | ✅ | max 255 | Original filename |
| `mime_type` | string | ✅ | max 100 | MIME type |
| `size_bytes` | int | ✅ | ≥0 | File size |
| `processing_status` | string | ✅ | enum: pending, processing, completed, failed | Processing status |
| `created_at` | datetime | ✅ | UTC | Upload timestamp |

---

## ai_analyses

**Purpose:** Validated AI analysis results.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `complaint_id` | string | ✅ | — | Analyzed complaint |
| `pipeline_version` | string | ✅ | max 50 | Pipeline version |
| `provider` | string | ✅ | max 50 | AI provider |
| `model` | string | ✅ | max 100 | Model identifier |
| `status` | string | ✅ | enum: pending, processing, completed, failed | Analysis status |
| `result` | dict | — | — | Structured result |
| `confidence` | float | — | 0-1 | Confidence score |
| `created_at` | datetime | ✅ | UTC | Creation timestamp |
| `completed_at` | datetime | — | UTC | Completion timestamp |
| `error_message` | string | — | max 1000 | Error details (no secrets) |

---

## incident_clusters

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `category` | string | — | enum: CivicCategory | Cluster category |
| `complaint_ids` | array[string] | ✅ | — | Member complaints |
| `complaint_count` | int | ✅ | ≥0 | Denormalized count |
| `representative_location` | GeoJSON Point | — | — | Cluster centroid |
| `radius_meters` | float | — | ≥0 | Cluster radius |
| `algorithm_version` | string | — | max 50 | Algorithm version |
| `created_at` | datetime | ✅ | UTC | Creation timestamp |
| `updated_at` | datetime | ✅ | UTC | Last update timestamp |

---

## assignments

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `complaint_id` | string | ✅ | — | Assigned complaint |
| `department_id` | string | ✅ | — | Assigned department |
| `assigned_to` | string | — | — | Specific user |
| `assigned_by` | string | ✅ | — | Assigning user |
| `status` | string | ✅ | enum: active, reassigned, completed | Status |
| `assigned_at` | datetime | ✅ | UTC | Assignment timestamp |
| `updated_at` | datetime | ✅ | UTC | Last update |

---

## status_history

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `complaint_id` | string | ✅ | — | Complaint reference |
| `previous_status` | string | — | enum: ComplaintStatus | Previous status |
| `new_status` | string | ✅ | enum: ComplaintStatus | New status |
| `actor_id` | string | — | — | User who triggered |
| `reason` | string | — | max 1000 | Reason/comment |
| `created_at` | datetime | ✅ | UTC | Transition timestamp |

---

## notifications

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `recipient_id` | string | ✅ | — | Recipient user |
| `type` | string | ✅ | enum: status_update, assignment, system | Type |
| `title` | string | ✅ | max 200 | Title |
| `message` | string | — | max 1000 | Message |
| `reference_id` | string | — | — | Related resource ID |
| `reference_type` | string | — | max 50 | Resource type |
| `status` | string | ✅ | enum: unread, read | Read state |
| `created_at` | datetime | ✅ | UTC | Creation timestamp |

---

## predictions

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `prediction_type` | string | ✅ | enum: hotspot, trend, recurrence | Type |
| `model_version` | string | ✅ | max 50 | Model version |
| `data_window_start` | datetime | ✅ | — | Data window start |
| `data_window_end` | datetime | ✅ | — | Data window end |
| `result` | dict | ✅ | — | Structured result |
| `confidence` | float | — | 0-1 | Confidence |
| `status` | string | ✅ | enum: active, expired, superseded | Status |
| `generated_at` | datetime | ✅ | UTC | Generation timestamp |
| `expires_at` | datetime | — | UTC | Expiration |

---

## audit_logs

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `_id` | ObjectId | auto | — | Document ID |
| `actor_id` | string | — | — | User (None for system) |
| `action` | string | ✅ | max 100 | Action identifier |
| `resource_type` | string | ✅ | max 50 | Affected resource type |
| `resource_id` | string | ✅ | — | Affected resource ID |
| `metadata` | dict | — | — | Additional context (no secrets) |
| `created_at` | datetime | ✅ | UTC | Action timestamp |
