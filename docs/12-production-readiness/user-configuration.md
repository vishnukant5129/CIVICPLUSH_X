# Final User Configuration & Credentials Guide

This document lists all environment variables and credentials required to run CivicPulse AI in local Docker development or production.

## Final AI Provider: Google Gemini
The final production LLM provider for CivicPulse AI is **Google Gemini**. Groq is NOT used as the final AI provider.

## Environment Variables Inventory

| Variable | Purpose | Local Docker Default | Production Requirement | Secret? | Where to Obtain |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `GEMINI_API_KEY` | API Key for Google Gemini LLM complaint processing | Required for LLM features | **REQUIRED** | **YES** | [Google AI Studio](https://aistudio.google.com/) |
| `GEMINI_MODEL` | Google Gemini LLM model identifier | `gemini-3.6-flash` | Configurable | No | [Gemini Model Docs](https://ai.google.dev/models/gemini) |
| `APP_ENV` | Application environment (`development`, `production`, `test`) | `development` | `production` | No | Internal configuration |
| `APP_DEBUG` | Enable debug mode (must be `false` in production) | `false` | `false` | No | Internal configuration |
| `MONGODB_URI` | Connection URI for MongoDB | `mongodb://mongodb:27017/civicpulse` | `mongodb+srv://...` | Yes (in Prod) | Local Docker or MongoDB Atlas |
| `MONGODB_DATABASE` | Database name | `civicpulse` | `civicpulse` | No | Internal configuration |
| `REDIS_URL` | Connection URL for Redis session store | `redis://redis:6379/0` | `redis://...` | Yes (in Prod) | Local Docker or Redis Cloud |
| `CORS_ORIGINS` | Allowed origins (comma-separated list) | `http://localhost:5173` | `https://your-domain.com` | No | Infrastructure setup |
| `FRONTEND_URL` | Deployed frontend application URL | `http://localhost:5173` | `https://your-domain.com` | No | Infrastructure setup |
| `VITE_API_BASE_URL` | Frontend API base URL | `http://localhost:8000` | `https://api.your-domain.com` | No | Infrastructure setup |

## Local Docker Mode vs Production

- **Local Docker Mode (`docker compose up --build`)**:
  - MongoDB and Redis run automatically inside Docker containers.
  - `MONGODB_URI` defaults to `mongodb://mongodb:27017/civicpulse` (No Atlas credentials required).
  - `REDIS_URL` defaults to `redis://redis:6379/0` (No external Redis credentials required).
  - `GEMINI_API_KEY` is required in `.env` for LLM analysis.

- **Production Mode**:
  - Supply production MongoDB Atlas URI (`MONGODB_URI`), production Redis URI (`REDIS_URL`), `GEMINI_API_KEY`, and production `CORS_ORIGINS`.

## Credentials NOT Required
- **Hugging Face Token**: Not required (`sentence-transformers/all-MiniLM-L6-v2` auto-downloads locally).
- **Map API Key**: Not required (Leaflet + OpenStreetMap tiles used directly).
- **Cloud Storage Credentials**: Not required for local MVP (Local disk / Docker volume `uploads_data`).
- **Auth Secrets**: Not required (Opaque session tokens generated server-side).
