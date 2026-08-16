# Similarity Model & Duplicate Detection

## Duplicate vs. Related
Civic incidents vary heavily in semantics. Two individuals reporting identical potholes are `DUPLICATES`. One citizen reporting a "Burst Pipe" while another reports "Flooded Intersection" exactly 50 meters away might be `RELATED`.

We execute heuristic classification utilizing absolute boundaries:
1. `DUPLICATE`: Semantic Similarity >= `0.85` AND geographic distance <= `200m`.
2. `RELATED`: Semantic Similarity >= `0.70` AND geographic distance <= `1000m`.
3. `INDEPENDENT`: Temporal mismatch exceeding 30 days OR falling below the similarity thresholds.

## Explainability
The backend returns deterministic justification phrases for relationship boundaries.
For example, it might inject the phrase "High semantic similarity but distinct geographic locations." This provides user context without relying entirely on raw float parameters. 

We deliberately DO NOT map similarity heuristics to a deterministic "probability %". Model confidence is fundamentally not equivalent to probabilistic ground-truth accuracy.
