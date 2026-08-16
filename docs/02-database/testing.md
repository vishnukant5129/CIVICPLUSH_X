# CivicPulse AI — Phase 2 Testing

## Test Structure

| Test File | Count | Scope |
|-----------|-------|-------|
| `test_config.py` | 16 | Configuration validation (Phase 1) |
| `test_database.py` | 6 | MongoDB/Redis health checks (Phase 1) |
| `test_health.py` | 9 | Health/readiness endpoints (Phase 1) |
| `test_enums.py` | 12 | Domain enum values and consistency |
| `test_schemas.py` | 31 | Pydantic schema validation rules |
| `test_repositories.py` | 17 | Repository CRUD, pagination, error handling |
| `test_init_db.py` | 9 | Index creation, collection names, idempotency |

**Total: 109 tests, all passing.**

## Test Isolation

- All tests run with `APP_ENV=test`
- `MONGODB_URI` and `REDIS_URL` are empty in test environment
- MongoDB/Redis connections are mocked in integration tests
- Repository tests use mocked `AsyncCollection` — no real DB
- Schema tests are pure Pydantic validation — no DB or network
- No test connects to any real database

## Running Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

## What's Tested

### Schemas (test_schemas.py)
- GeoJSON coordinate validation (longitude -180 to 180, latitude -90 to 90)
- Boundary values accepted
- Wrong types rejected
- User email format, normalized email lowercase
- Display name min/max length
- Complaint title/description min/max length
- Priority score range (0-100)
- Invalid category rejected
- All complaint statuses accepted
- Evidence negative size rejected
- Status history transition with/without previous status
- Audit log with/without actor

### Repositories (test_repositories.py)
- ObjectId ↔ string serialization
- Invalid ID handling
- Insert returns string ID
- DuplicateKeyError → DuplicateDocumentError with field name
- PyMongoError → RepositoryError
- find_by_id serializes correctly, returns None when not found
- find_many pagination (capped at 200, minimum 1)
- update_one returns True/False
- delete_one returns True/False

### Database Init (test_init_db.py)
- Collection names are lowercase snake_case
- All 11 collection names are correct
- ensure_indexes runs without errors
- Creates user unique email index
- Creates complaint geospatial index
- Creates department unique code index
- All 11 collections receive indexes
- Idempotent (double call succeeds)
