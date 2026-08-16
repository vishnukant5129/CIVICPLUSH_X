# Dashboard API

## Endpoints

### 1. Summary API
`GET /api/v1/dashboard/summary`
- Authenticated: YES
- Parameters: `status`, `category`, `date_from`, `date_to`
- Returns: `DashboardSummaryResponse` (Total, by status, by category, trend, AI stats).

### 2. Map API
`GET /api/v1/dashboard/complaints/map`
- Authenticated: YES
- Parameters: `status`, `category`, `date_from`, `date_to`
- Returns: `GeoJSONFeatureCollection`

Both endpoints extract `user_id` strictly from the internal session parameter and merge it at the root of the database query.
