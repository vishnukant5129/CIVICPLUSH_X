# Testing

`test_intelligence.py` asserts the boundaries of the API endpoints, isolating the service mock logic effectively to confirm HTTP response isolation.
We ensure `403 Forbidden` errors natively deploy if a user attempts to fetch metadata on unowned resource configurations.
