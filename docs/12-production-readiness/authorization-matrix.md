# Endpoint Authorization Matrix

| Endpoint | Unauthenticated | CITIZEN | AUTHORITY | ADMIN |
| :--- | :---: | :---: | :---: | :---: |
| `POST /api/v1/auth/register` | ALLOW | DENY | DENY | DENY |
| `POST /api/v1/auth/login` | ALLOW | DENY | DENY | DENY |
| `POST /api/v1/auth/logout` | DENY | ALLOW | ALLOW | ALLOW |
| `GET /api/v1/auth/me` | DENY | ALLOW | ALLOW | ALLOW |
| `POST /api/v1/complaints/` | DENY | ALLOW | ALLOW | ALLOW |
| `GET /api/v1/complaints/` | DENY | ALLOW (Own) | ALLOW (Scope) | ALLOW (Global) |
| `GET /api/v1/complaints/{id}` | DENY | ALLOW (Own) | ALLOW (Scope) | ALLOW (Global) |
| `GET /api/v1/authority/dashboard/summary` | DENY | DENY (403) | ALLOW (Scope) | ALLOW (Global) |
| `GET /api/v1/authority/complaints` | DENY | DENY (403) | ALLOW (Scope) | ALLOW (Global) |
| `POST /api/v1/authority/complaints/{id}/assign` | DENY | DENY (403) | ALLOW | ALLOW |
| `POST /api/v1/authority/complaints/{id}/status` | DENY | DENY (403) | ALLOW | ALLOW |
| `GET /api/v1/authority/evidence/{id}/download` | DENY | ALLOW (Own) | ALLOW (Scope) | ALLOW (Global) |
| `GET /api/v1/predictions/summary` | DENY | ALLOW | ALLOW | ALLOW |
| `GET /api/v1/predictions/hotspots` | DENY | DENY (403) | ALLOW | ALLOW |
| `POST /api/v1/predictions/generate` | DENY | DENY (403) | ALLOW | ALLOW |
| `GET /api/v1/notifications/` | DENY | ALLOW (Own) | ALLOW (Own) | ALLOW (Own) |
