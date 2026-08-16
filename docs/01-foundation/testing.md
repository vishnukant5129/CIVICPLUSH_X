# CivicPulse AI — Testing

## Framework

- **pytest** with **pytest-asyncio** for async test support
- **httpx** `AsyncClient` with `ASGITransport` for FastAPI integration tests

## Test Isolation

- All tests run with `APP_ENV=test`
- `MONGODB_URI` and `REDIS_URL` are set to empty strings in test environment
- MongoDB and Redis connections are mocked in integration tests
- No test connects to production or development databases

## Running Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

## Test Coverage (Phase 1)

| Test File | Tests | Covers |
|-----------|-------|--------|
| `test_config.py` | 16 | Default values, production validation, debug blocking, log levels, CORS parsing, environment properties |
| `test_health.py` | 8 | Health endpoint, readiness endpoint, error handling, security (no credential leaks) |
| `test_database.py` | 7 | MongoDB/Redis connectivity checks (mocked, no real connections) |

**Total: 31 tests, all passing.**

## Test Principles

1. No test uses fake production data
2. No test connects to a real database
3. Infrastructure checks are tested with mocked clients
4. Error handling is verified to produce safe responses
5. Security checks verify no credentials leak in responses
