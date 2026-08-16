# CivicPulse AI — Repository Design

## Architecture

```
Routes (Phase 3+)
    ↓
Services (Phase 3+)
    ↓
Repositories ← Phase 2
    ↓
MongoDB (PyMongo Async)
```

## Design Principles

1. **Repositories contain only database logic** — no HTTP handling, no authorization, no AI/LLM logic.
2. **BaseRepository** provides reusable CRUD, pagination, and geospatial query primitives.
3. **Collection repositories** extend `BaseRepository` with domain-specific queries.
4. **Error translation** — raw `PyMongoError` → `RepositoryError` hierarchy. Clients never see driver exceptions.
5. **ID serialization** — MongoDB `_id` (ObjectId) → string `id`. Consumers never see raw ObjectIds.
6. **Pagination is safe** — limit capped at 200, minimum 1. No unbounded collection retrieval.

## Error Hierarchy

```
RepositoryError (base)
├── DocumentNotFoundError
├── DuplicateDocumentError (includes violated field name)
└── InvalidIdError
```

## Repository Inventory

| Repository | Collection | Key Methods |
|------------|-----------|-------------|
| `UserRepository` | users | `find_by_email()` |
| `DepartmentRepository` | departments | `find_by_code()`, `find_active()` |
| `ComplaintRepository` | complaints | `find_by_user()`, `find_by_status()`, `find_nearby()`, `find_by_cluster()` |
| `EvidenceRepository` | evidence | `find_by_complaint()` |
| `AIAnalysisRepository` | ai_analyses | `find_latest_for_complaint()`, `find_by_complaint()` |
| `IncidentClusterRepository` | incident_clusters | `find_by_category()` |
| `AssignmentRepository` | assignments | `find_by_complaint()`, `find_active_by_department()` |
| `StatusHistoryRepository` | status_history | `find_by_complaint()` |
| `NotificationRepository` | notifications | `find_by_recipient()`, `count_unread()` |
| `PredictionRepository` | predictions | `find_active()` |
| `AuditLogRepository` | audit_logs | `find_by_resource()`, `find_by_actor()` |

## Base CRUD Methods

All repositories inherit:

| Method | Description |
|--------|-------------|
| `insert_one(doc)` | Insert document, return string ID |
| `find_by_id(id)` | Find by ID, return serialized doc or None |
| `find_one(filter)` | Find single doc by filter |
| `find_many(filter, sort, skip, limit)` | Paginated query |
| `count(filter)` | Count matching documents |
| `update_one(id, update)` | Update by ID |
| `update_many(filter, update)` | Batch update |
| `delete_one(id)` | Delete by ID |
| `find_near(field, lon, lat, max_dist)` | Geospatial $near query |

## Usage Pattern (for future phases)

```python
from app.database.mongodb import get_database
from app.repositories.collections import ComplaintRepository

db = get_database()
repo = ComplaintRepository(db)

# Insert
doc_id = await repo.insert_one(complaint_dict)

# Query
complaint = await repo.find_by_id(doc_id)
nearby = await repo.find_nearby(77.1025, 28.7041, max_distance_meters=1000)
```
