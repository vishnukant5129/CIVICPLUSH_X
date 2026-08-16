# Scoring and Thresholds

All constants are parameterized via `app.config`.

## Definitions
- `candidate_search_limit` (50): Limits MongoDB candidate retrievals.
- `geo_candidate_radius_meters` (1000): Haversine constraint for querying surrounding data objects.
- `duplicate_similarity_threshold` (0.85): Minimum Cosine boundary for exact duplication classification.
- `related_similarity_threshold` (0.70): Minimum Cosine boundary for neighborhood civic anomalies.
- `temporal_proximity_days` (30): Absolute time-cap separating independent civic anomalies.
