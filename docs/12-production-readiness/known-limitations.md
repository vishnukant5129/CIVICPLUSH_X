# Known Limitations & MVP Deferred Boundaries

1. **Downstream Municipal Integration**:
   - The government integration adapter (`GovernmentIntegrationAdapter`) reports truthful integration status (`NOT_CONFIGURED`) when external municipal system credentials or API webhooks are unconfigured. No fake external delivery confirmations are generated.

2. **Single-Node Local File Evidence Storage**:
   - Evidence files are currently persisted to local disk storage (`uploads/{complaint_id}/`) behind protected API endpoints. Object storage integration (S3/GCS) can be configured via environment settings for production cloud deployments.

3. **Background Worker Execution**:
   - In single-node development, background tasks (AI analysis, notifications, and embedding calculations) execute via asynchronous event loop tasks (`asyncio.create_task`) or RQ worker queue if Redis queue is active.
