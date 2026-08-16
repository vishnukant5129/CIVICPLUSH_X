# Testing Strategy for Complaints

## Backend Tests (`tests/test_complaints.py`)

Using mocked authentication and mocked database instances to ensure rapid, isolated execution.

### `TestComplaintCreation`
- **Success:** Verifies valid requests successfully create a `ComplaintDocument` and a corresponding `StatusHistoryDocument`.
- **Server Control:** Verifies that the service enforces the authenticated `user_id` regardless of payload, and that `status` defaults to `SUBMITTED`.

### `TestComplaintOwnership`
- **Isolation:** Attempts to fetch a complaint belonging to a different user, verifying a strict `404 Not Found` response.
- **Listing:** Mocks the user ID and ensures `/my` executes `get_user_complaints` using exclusively that authenticated user ID.

## Frontend
No formal frontend test files are added in this phase, as we rely on Vite's build compilation (`tsc -b && vite build`) to ensure type safety and structural correctness of the React components (`ComplaintForm`, `MyComplaints`, `ComplaintDetail`).
