# CivicPulse AI — Environment Configuration

## Environment Variables

All configuration is managed through environment variables loaded via `.env` files.

### Setup

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

### Required Variables

| Variable | Required In | Description |
|----------|-------------|-------------|
| `APP_ENV` | All | Environment: `development`, `test`, `production` |
| `MONGODB_URI` | Production | MongoDB Atlas connection string |
| `MONGODB_DATABASE` | All | Database name (default: `civicpulse`) |
| `REDIS_URL` | When Redis enabled | Redis connection URL |
| `CORS_ORIGINS` | All | Comma-separated allowed origins |
| `LOG_LEVEL` | All | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

### Environment Behavior

| Behavior | Development | Test | Production |
|----------|------------|------|------------|
| MongoDB URI | Optional (warns if empty) | Optional (mocked in tests) | **Required** (fails without it) |
| Debug mode | Allowed | Allowed | **Blocked** |
| API docs (`/docs`) | Enabled | Enabled | Disabled |
| Log format | Human-readable | Human-readable | JSON structured |
| CORS | Configured origins | Test origins | Strictly configured |

### Frontend Environment

The frontend uses `VITE_`-prefixed variables only:

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend API URL (default: `http://localhost:8000`) |

**SECURITY:** No server-side secrets (`MONGODB_URI`, `REDIS_URL`, etc.) are exposed to the browser.

### Configuration Validation

Configuration validation runs at application startup:
- Missing `MONGODB_URI` in production → clear error message
- `APP_DEBUG=true` in production → blocked
- Invalid `LOG_LEVEL` → rejected with allowed values listed
