# Security

## Scope Isolation
- `user_id` is forcefully inserted into the `$match` aggregation pipeline at the inception of `DashboardService._build_match_query`.
- All requests naturally filter down to identical domains (user-owned data).
- The map queries exclusively user-owned constraints and therefore guarantees zero cross-user spatial leakage.

## Query Injection Protection
The `DashboardFilters` object maps directly into structured Pydantic parameters. We evaluate `date_from` and `date_to` by explicitly parsing them into datetime primitives before transmitting to MongoDB. Unrecognized keys are omitted, eliminating NOSQL injection vulnerabilities.
