# CIVICPLUSH_X — CivicPulse AI

CivicPulse AI is an AI-powered civic intelligence platform that empowers citizens to report civic issues and enables government authorities to manage, route, and analyze civic complaints with predictive analytics and geospatial clustering.

---

## 🚀 Quick Start — One-Command Unified Docker Stack

The entire CivicPulse AI system (Frontend, Backend, MongoDB, and Redis) can be launched using a single Docker Compose command:

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine v24+ with Docker Compose v2+.

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional: Add your `GROQ_API_KEY` in `.env` for AI LLM complaint analysis).*

### 3. Launch Stack
Run the unified Docker stack:
```bash
docker compose up --build
```

---

## 🌐 Container Services & Exposed Host Ports

| Service | Internal Container Port | Host URL / Port | Container Name | Health Check |
| :--- | :---: | :---: | :--- | :--- |
| **Frontend** | 5173 | [http://localhost:5173](http://localhost:5173) | `civicpulse-frontend` | HTTP GET `/` |
| **Backend API** | 8000 | [http://localhost:8000](http://localhost:8000) | `civicpulse-backend` | HTTP GET `/health` |
| **MongoDB** | 27017 | `localhost:27017` | `civicpulse-mongodb` | `mongosh ping` |
| **Redis** | 6379 | `localhost:6379` | `civicpulse-redis` | `redis-cli ping` |

---

## 💾 Data & Storage Persistence

The Docker stack utilizes named volumes so data survives container restarts:
- `mongodb_data`: Persists MongoDB database records.
- `redis_data`: Persists session store state.
- `uploads_data`: Persists citizen uploaded evidence files (`/app/uploads`).

### Stopping the Stack
To stop the containers while preserving all database records and uploads:
```bash
docker compose down
```

To stop containers and reset database volumes:
```bash
docker compose down -v
```

---

## 🧪 Local Testing & Verification

### Run Backend Unit & Integration Tests:
```bash
cd backend
source .venv/bin/activate
python -m pytest -v
```

### Build Frontend SPA Bundle:
```bash
cd frontend
npm run build
```
