# CivicPulse AI — Infrastructure

## Docker Compose

### Services

| Service | Image | Purpose |
|---------|-------|---------|
| `backend` | Custom (Python 3.12) | FastAPI application |
| `frontend` | Custom (Node 22) | React + Vite dev server |
| `redis` | `redis:7-alpine` | Background processing infrastructure |

### No Local MongoDB

CivicPulse uses **MongoDB Atlas** as its primary database. No local MongoDB container is included.

Set `MONGODB_URI` in your `.env` file to connect to your Atlas cluster.

### Running

```bash
# Validate configuration
docker compose config

# Start all services
docker compose up

# Start with rebuild
docker compose up --build

# Stop
docker compose down
```

### Health Checks

| Service | Health Check | Interval |
|---------|-------------|----------|
| Backend | `curl -f http://localhost:8000/health` | 30s |
| Redis | `redis-cli ping` | 10s |

### Running Without Docker

```bash
# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## MongoDB Atlas

- **Driver:** PyMongo Async (modern async API)
- **Phase 1:** Connection lifecycle only. No domain collections created.
- **Connectivity:** Verified via real `ping` command, not fake responses.

## Redis

- **Driver:** redis-py async
- **Phase 1:** Connection lifecycle only. No background jobs implemented.
- **Connectivity:** Verified via real `ping` command.
