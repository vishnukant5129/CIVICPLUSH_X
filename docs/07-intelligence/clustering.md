# Incident Clustering

## Algorithm: Connected Components
Instead of utilizing fixed centroid logic (like K-Means) which forces predetermined quantities of unrelated variables to cluster improperly, we mapped Civic incidents dynamically using connected graphs.

The graph evaluates every validated `DUPLICATE` and `RELATED` complaint edge. By calculating depth-first component paths natively on the backend, civic anomalies that spiral outward linearly (like a damaged power line stretching over 3 blocks with 6 distinct complaints) securely chain together into a solitary deterministic `CLUSTER-XXXXXXXX` UUID group.
