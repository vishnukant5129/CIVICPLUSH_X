# Dashboard Architecture

The dashboard relies on an isolated `DashboardService` that interacts directly with MongoDB to perform server-side aggregations.

## Request Lifecycle
1. Citizen visits `/dashboard`.
2. React frontend sends parallel API requests to `/api/v1/dashboard/summary` and `/api/v1/dashboard/complaints/map`.
3. Backend extracts the `user_id` from the session.
4. `DashboardService` constructs a root `$match` filter query.
5. MongoDB evaluates the query, processes the `$facet` aggregation to compute totals, and returns the optimized dataset.
6. The frontend renders the data components (Cards, Lists, Charts, Maps). Empty states are rendered dynamically if the data is fundamentally zero.

## Performance
We actively avoid N+1 querying. We utilize MongoDB's `$facet` operator to process multiple sub-pipelines simultaneously.
