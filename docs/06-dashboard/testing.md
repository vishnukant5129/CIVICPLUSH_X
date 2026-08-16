# Testing

The backend test suite verifies that `DashboardService` is securely scoped via isolated, mock HTTP client parameters.

`tests/test_dashboard.py` evaluates:
- `/api/v1/dashboard/summary`
- `/api/v1/dashboard/complaints/map`

The integration explicitly patches `AuthService.get_session` to mock a `citizen_a` session and asserts that the downstream MongoDB service calls encapsulate `user_id=user_a`.
