# Auth API Contract

Base URL: `/api/v1/auth`

---

## 1. Register User

**POST** `/register`

- **Auth Required:** No
- **Roles Allowed:** Public
- **Description:** Registers a new `CITIZEN`. Forces role to `CITIZEN`. Automatically logs in the user and sets a session cookie.

**Request Body:**
```json
{
  "email": "user@example.com",
  "display_name": "Test User",
  "password": "StrongPassword123!"
}
```

**Response (201 Created):**
```json
{
  "id": "507f191e810c19729de860ea",
  "email": "user@example.com",
  "display_name": "Test User",
  "role": "citizen",
  "department_id": null
}
```

**Errors:**
- `409 Conflict`: Email already exists.
- `422 Unprocessable Entity`: Validation failure.

---

## 2. Login

**POST** `/login`

- **Auth Required:** No
- **Roles Allowed:** Public
- **Description:** Verifies credentials, creates a Redis session, and sets the `civicpulse_session` HttpOnly cookie.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

**Response (200 OK):**
```json
{
  "id": "...",
  "email": "user@example.com",
  "display_name": "Test User",
  "role": "citizen",
  "department_id": null
}
```

**Errors:**
- `401 Unauthorized`: Invalid email or password.

---

## 3. Get Current User

**GET** `/me`

- **Auth Required:** Yes
- **Roles Allowed:** All
- **Description:** Returns the public profile of the currently authenticated user based on the session cookie.

**Response (200 OK):**
```json
{
  "id": "...",
  "email": "user@example.com",
  "display_name": "Test User",
  "role": "citizen",
  "department_id": null
}
```

**Errors:**
- `401 Unauthorized`: Missing or invalid session.

---

## 4. Logout

**POST** `/logout`

- **Auth Required:** Optional (No-op if unauthenticated)
- **Roles Allowed:** All
- **Description:** Destroys the session in Redis and clears the client's session cookie.

**Response (204 No Content)**
