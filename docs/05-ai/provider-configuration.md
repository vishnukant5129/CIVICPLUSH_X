# Provider Configuration

## AI Provider Settings
The AI Provider is configured via environment variables.

- `AI_PROVIDER`: The backend provider (defaults to `groq`).
- `GROQ_API_KEY`: Required if provider is `groq`. Without this, the upload succeeds but AI analysis marks as `FAILED` with an unconfigured error.
- `AI_MODEL`: The LLM to target (defaults to `llama3-8b-8192` for Groq).

## Storage Provider Settings
- `STORAGE_PATH`: Directory to store local evidence (defaults to `uploads`).
- `MAX_UPLOAD_SIZE_BYTES`: Enforced upload size limit (defaults to 10MB).
