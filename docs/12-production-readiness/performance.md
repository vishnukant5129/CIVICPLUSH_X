# Performance & Bounded Constraints Audit

## 1. Database Indexes
MongoDB indexes are automatically verified and ensured during application startup (`ensure_indexes`):
- `users`: `normalized_email` (unique)
- `complaints`: `user_id + created_at`, `status + priority_score`, `location.geo` (2dsphere geospatial index)
- `assignments`: `complaint_id`, `department_id + status`
- `status_history`: `complaint_id + created_at`
- `authority_audit_trail`: `complaint_id + created_at`
- `notifications`: `user_id + is_read + created_at`
- `predictions`: `prediction_type + generated_at`

## 2. Bounded Query Limits
- **Complaint Queue**: Hard-capped server-side pagination with `page_size` max limit of 100 items.
- **Aggregation Limits**: Summaries and geographic cluster aggregations are limited to top 200 elements to bound memory consumption.
- **Candidate Vector Search**: Candidate similarity searches are capped at `candidate_search_limit` (50 records).

## 3. ML Model Initialization Memory Management
- `SentenceTransformer` models are loaded lazily upon first vector calculation and reused in singleton memory state across API invocations.
- Vector calculations operate on 384-dimensional dense float arrays (`all-MiniLM-L6-v2`), bounding RAM overhead per request.
