# CivicPulse AI — Data Modeling Decisions

## 1. Embedded vs Referenced Documents

### Location → Embedded in Complaint
- **Decision:** Embed `LocationData` (including GeoJSON point) inside complaint documents.
- **Reason:** Location is owned by the complaint, always accessed together, and immutable after submission. Embedding avoids a join for every spatial query.
- **Trade-off:** Slightly larger complaint documents, but spatial queries can use the embedded `location.geo` field directly with a 2dsphere index.

### Evidence → Separate Collection (referenced by complaint_id)
- **Decision:** Store evidence as separate documents referencing `complaint_id`.
- **Reason:** Multiple evidence items per complaint, each with its own processing lifecycle and potentially large metadata. Independent processing status. Embedding would bloat complaint documents and make evidence-specific queries harder.

### AI Analysis → Separate Collection (referenced by complaint_id)
- **Decision:** Store AI analysis results as separate documents.
- **Reason:** Multiple analysis runs possible (retries, version upgrades), independent processing status. Should not bloat complaint documents. Allows querying analysis results independently.

### Status History → Separate Collection (referenced by complaint_id)
- **Decision:** Append-only status history in a separate collection.
- **Reason:** Unbounded growth (many transitions per complaint). Queried independently for timeline views. Embedding would cause complaint documents to grow unboundedly.

---

## 2. ID Strategy

- **Decision:** Use MongoDB native `ObjectId` as `_id`.
- **Reason:** Built-in uniqueness, timestamp-embedded (supports rough chronological ordering), well-supported by PyMongo, compatible with MongoDB indexes and sharding.
- **Serialization:** Repository layer converts `_id` (ObjectId) to `id` (string) in application code. API consumers never see raw ObjectIds.
- **Alternatives considered:** UUID v4 (portable but no ordering), custom snowflake IDs (unnecessary complexity for MVP).

---

## 3. Timestamp Strategy

- **Decision:** All timestamps stored in UTC as `datetime` objects.
- **Convention:** `created_at` for creation, `updated_at` for last modification.
- **Reason:** UTC avoids timezone ambiguity in a multi-user system. Presentation layers convert to local timezone.
- **Implementation:** `datetime.now(timezone.utc)` via `_utcnow()` helper in schemas.

---

## 4. Category Representation

- **Decision:** Application-controlled Python enum (`CivicCategory`), not database-backed entities.
- **Reason:** The PRD defines a fixed initial category set that is structural to the AI classification pipeline and routing logic. Adding a category requires code changes to classification prompts and routing rules. Database-backed dynamic categories would create false flexibility without actual runtime benefit in MVP.
- **Future migration:** If post-MVP requirements demand user-defined categories, migration to database-backed entities can be performed.

---

## 5. Department Representation

- **Decision:** Database-backed entities in the `departments` collection.
- **Reason:** Departments are managed through the application by admins, not hardcoded. Different deployments may have different department configurations. Unique `code` constraint enforces integrity.

---

## 6. Email Uniqueness

- **Decision:** Unique index on `normalized_email` (lowercase).
- **Reason:** Email uniqueness must be enforced at the database level, not just application code. Normalizing to lowercase ensures `User@Example.com` and `user@example.com` are treated as the same identity.
- **Implementation:** Application sets `normalized_email = email.lower()`. Database enforces uniqueness via unique index.

---

## 7. Cluster Membership and Denormalized Count

- **Decision:** `incident_clusters.complaint_ids` is the authoritative member list. `complaint_count` is denormalized for dashboard display.
- **Reason:** Dashboard queries that list clusters with counts would otherwise require aggregation on every request. The denormalized count avoids this.
- **Trade-off:** `complaint_count` must be updated transactionally with membership changes. If it drifts, it can be recalculated from `complaint_ids.length`.
- **Strategy:** Future cluster update operations must update both `complaint_ids` and `complaint_count` atomically.

---

## 8. Evidence Count on Complaint

- **Decision:** `complaints.evidence_count` is denormalized.
- **Reason:** Displaying evidence count on complaint lists without querying the evidence collection. Authoritative count is from the `evidence` collection.
- **Trade-off:** Must be updated when evidence is added/removed.

---

## 9. Collection Naming

- **Decision:** Lowercase snake_case for all collection names.
- **Reason:** Consistency, readability, and alignment with Python naming conventions.
- **Names:** `users`, `departments`, `complaints`, `evidence`, `ai_analyses`, `incident_clusters`, `assignments`, `status_history`, `notifications`, `predictions`, `audit_logs`.

---

## 10. Schema Evolution / Migration

- **Decision:** No formal migration system in Phase 2.
- **Reason:** MongoDB's schema-flexible nature and the fact that we're in early development. Index changes are managed through idempotent `ensure_indexes()`.
- **Strategy for future:** Schema changes should be documented in CHANGELOG.md. Destructive changes (renaming/removing fields) require explicit migration scripts. Adding new optional fields is backward-compatible and requires no migration.
