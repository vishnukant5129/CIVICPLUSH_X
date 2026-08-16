# Complaints API Contract

Base URL: `/api/v1/complaints`

---

## 1. Create Complaint

**POST** `/`

- **Auth Required:** Yes
- **Roles Allowed:** `CITIZEN`
- **Ownership:** Bound to the authenticated user derived from the session.

**Request Body (`ComplaintCreateRequest`):**
```json
{
  "title": "Pothole on Main St",
  "description": "Huge pothole causing traffic issues.",
  "category": "pothole_road_damage",
  "location": {
    "geo": {
      "type": "Point",
      "coordinates": [77.2090, 28.6139]
    },
    "address": "Main St, New Delhi"
  }
}
```

**Response (201 Created) - `ComplaintResponse`:**
```json
{
  "id": "complaint_id",
  "user_id": "auth_user_id",
  "title": "Pothole on Main St",
  "description": "Huge pothole causing traffic issues.",
  "category": "pothole_road_damage",
  "location": { ... },
  "status": "submitted",
  "evidence_count": 0,
  "created_at": "2026-08-16T10:00:00Z",
  "updated_at": "2026-08-16T10:00:00Z"
}
```

---

## 2. List My Complaints

**GET** `/my`

- **Auth Required:** Yes
- **Roles Allowed:** `CITIZEN`
- **Ownership:** Only returns complaints where `user_id` matches the authenticated user.

**Response (200 OK):**
List of `ComplaintResponse` objects.

---

## 3. Get Complaint Detail

**GET** `/{complaint_id}`

- **Auth Required:** Yes
- **Roles Allowed:** `CITIZEN`
- **Ownership:** Returns `404 Not Found` if the complaint does not exist OR if it belongs to another user.

**Response (200 OK):**
`ComplaintResponse` object.

---

## 4. Get Status History

**GET** `/{complaint_id}/history`

- **Auth Required:** Yes
- **Roles Allowed:** `CITIZEN`
- **Ownership:** Returns `404 Not Found` if the complaint does not exist OR if it belongs to another user.

**Response (200 OK):**
List of `StatusHistoryResponse` objects.
