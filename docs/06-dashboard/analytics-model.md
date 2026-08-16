# Analytics Model

## Metrics Source
All analytic figures derived in the dashboard originate from real data.

1. `total_complaints`: Count of complaints satisfying the filter criteria for the authenticated user.
2. `with_evidence`: Tracks the number of complaints matching the filter criteria that have an `evidence_count > 0`.
3. `by_status`: Groups the matched complaints by the `status` enum field.
4. `by_category`: Groups the matched complaints by the `category` enum field.
5. `trend`: Aggregates complaints by `created_at` formatted to a daily resolution (`%Y-%m-%d`).
6. `ai_stats`: In a separate aggregation against `ai_analyses`, counts the statuses of analyses tied strictly to the filtered list of `complaint_ids`.

## Integrity Constraints
- Categories are bounded by the internal `CivicCategory` enum. We do not synthesize categories if they don't exist.
- AI Stats map against `COMPLETED`, `PROCESSING`, and `FAILED` dynamically based on genuine backend task execution traces.
