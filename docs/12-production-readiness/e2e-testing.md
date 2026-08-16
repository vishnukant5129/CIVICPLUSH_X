# End-to-End Testing & Verification

## 1. Verified User Journeys

### Citizen Journey
1. **Registration & Auth**: Register new user (`CITIZEN` role) → receive session cookie in Redis session store.
2. **Complaint Creation**: Submit complaint with title, description, category (`pothole_road_damage`), and GeoJSON location `[77.209, 28.613]`.
3. **Evidence Upload**: Upload image evidence → validated MIME type (`image/jpeg`) and size limit → metadata saved and file stored securely under `uploads/{complaint_id}/`.
4. **AI Processing**: Trigger AI understanding pipeline → valid JSON schema output parsed and persisted in `ai_analyses`.
5. **Notification Reception**: Status change fires `COMPLAINT_SUBMITTED` domain event → user receives in-app notification.
6. **Complaint View**: View own complaint list and detailed status history.

### Authority Journey
1. **Authority Auth**: Login as authority user (`AUTHORITY` role).
2. **Operational Queue**: Inspect department operational scope banner (`scope_note`) and query server-side complaint queue filtered by category and status.
3. **Case Management**: Inspect case details, evidence download link, AI analysis, and similarity intelligence.
4. **Status Update & Assignment**: Assign case to municipal department and update status (`SUBMITTED` → `ASSIGNED` → `IN_PROGRESS`). Verified append-only audit record created in `authority_audit_trail`.
5. **External Delivery**: Trigger downstream municipal delivery adapter → truthful response returned.

### Admin Journey
1. **Admin Auth**: Login as admin user (`ADMIN` role).
2. **Global Dashboard**: View global operational metrics across all departments, audit log entries, and predictive spatial hotspot risks.

## 2. Cross-User Security Isolation Verification
- Tested Citizen A attempting to read/modify Citizen B's complaint → returns `403 Forbidden` / `404 Not Found`.
- Tested Citizen attempting to access Authority summary (`/api/v1/authority/dashboard/summary`) or trigger hotspot predictions → returns `403 Forbidden`.
