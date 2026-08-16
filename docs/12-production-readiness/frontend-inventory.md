# Frontend Application & Route Inventory

## 1. Route Map

| URL Path | Component | Allowed Roles | Description |
| :--- | :--- | :--- | :--- |
| `/` | Landing / Welcome | All | Landing page with login/registration status. |
| `/dashboard` | `Dashboard` | `CITIZEN` | Citizen overview, complaint submission stats, analytics, and predictive trends. |
| `/authority` | `AuthorityDashboard` | `AUTHORITY`, `ADMIN` | Operational dashboard with queue, assignment, status transition, audit log, and spatial hotspots. |
| `/complaints` | `MyComplaints` | `CITIZEN` | Citizen list of submitted complaints with status tracking. |
| `/complaints/new` | `ComplaintForm` | `CITIZEN` | Interactive report form with geolocation picker and evidence upload. |
| `/complaints/:id` | `ComplaintDetail` | `CITIZEN` | Detailed view of a citizen complaint, AI analysis breakdown, evidence viewer, and status history. |

## 2. Shared Components
- `NotificationInbox.tsx`: Real-time notification polling dropdown displaying user alerts.
- `PredictiveIntelligence.tsx`: Mathematical volume trend chart and spatial hotspot risk component.
- `ProtectedRoute.tsx`: Route guard enforcing client-side authorization before component rendering.
