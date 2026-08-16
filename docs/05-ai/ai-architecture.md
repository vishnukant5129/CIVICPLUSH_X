# AI Architecture

## Execution Model
- **Trigger:** Evidence upload automatically schedules an AI analysis run.
- **Asynchronous:** The AI call is executed via `asyncio.create_task` so the HTTP response for the upload returns immediately.
- **Lifecycle:** A `PENDING`/`PROCESSING` document is created in `AIAnalysisDocument` before the LLM is queried. This allows the frontend to show a "loading" state safely.
- **Completion:** Upon successful JSON decoding, the state transitions to `COMPLETED` and the output is merged.
- **Failure:** If the API fails or JSON is malformed, the state becomes `FAILED`.

## Prompt & Output
The AI receives a rigid system prompt instructing it to return ONLY JSON.
The structured output contains:
- `category`: Re-classified category from text.
- `summary`: Concise 1-sentence summary.
- `severity_indicators`: List of extracted strings.
- `model_confidence`: Float (0-1).

If the model hallucinates a category, the service falls back to `OTHER`.
