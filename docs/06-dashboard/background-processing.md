# Background Processing

Phase 6 instructed us to assess migrating the AI Processing from `asyncio.create_task` to `Redis/RQ` for durable execution survivability.

## Limitation Documentation
We have explicitly **abstained** from porting Phase 5's AI Service to `Redis/RQ`.

### Rationale
1. `rq` operates natively as a synchronous queue processor.
2. Our AI integration heavily leverages `AsyncGroq` alongside asynchronous PyMongo engine commands (`motor`).
3. Forcing `rq` into this framework would necessitate stripping the asynchronous ecosystem out of the AI service, or spinning up disjoint sub-loops, which critically degrades Phase 5's baseline stability. 
4. Celery was forbidden by the prompt.

**Result:** `asyncio.create_task` remains. The consequence is that if the FastAPI backend unexpectedly crashes during an active LLM generation, the task is lost. The citizen will observe their task remaining perpetually in a `PROCESSING` state until an arbitrary reaper clears it in a future phase.
