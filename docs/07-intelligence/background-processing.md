# Background Processing

We continued to uphold the limitation of utilizing lightweight `asyncio.create_task()` executions to prevent blocking primary FastAPI threads while generating ML models.
Re-evaluating a migration to `Redis/RQ` confirmed our earlier rejection. Running Heavy localized ML structures (like `sentence-transformers`) within isolated Python synchronous instances heavily complicates our motor asynchronous configurations and drastically expands docker complexity constraints, which falls significantly out of scope for CivicPulse MVP boundaries. 
