# Intelligence Architecture

The architecture scales by pipelining generation and verification separately.

## Processing Flow
1. **Trigger:** `POST /api/v1/intelligence/complaints/{id}/process`
2. **Background Execution:** `asyncio.create_task` fires the idempotent `process_intelligence` pipeline.
3. **Embedding Strategy:** Complaint `title`, `description`, and `category` are concatenated and mathematically encoded into a 384-dimensional native vector using `sentence-transformers` locally, preventing external NLP API costs and latency.
4. **Candidate Generation:** Utilizing MongoDB's `$geoNear` 2dsphere index, we extract neighboring complaints to drastically limit evaluation to physically adjacent events.
5. **Similarity Check:** Evaluating geographic Haversine limits alongside cosine proximity of encoded vectors to categorize candidates securely.
6. **Relation Persistence:** `ComplaintRelation` models are dumped natively into MongoDB.
7. **Graph Recomputation:** Graph mapping updates disjoint groups via a Connected Components recursive cluster map and dynamically syncs valid clusters into the `incident_clusters` store.
