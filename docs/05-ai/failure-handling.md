# Failure Handling

## Evidence Upload Failure
- **Validation Failure:** HTTP 400 with a clear error if the file exceeds size limits or uses an unsupported MIME type.
- **Storage Failure:** If saving to disk fails, the database transaction is skipped, and HTTP 500 is returned. The complaint is untouched.

## AI Execution Failure
Because AI execution happens asynchronously, a failed LLM call does not fail the evidence upload. The result of the failure is stored safely.

- **Missing Keys:** Marked as `FAILED` with reason.
- **Malformed JSON:** The AI response couldn't be parsed. Marked as `FAILED`.
- **Timeouts / 5xx Provider Errors:** Caught by the generic exception handler, marked as `FAILED`.

## Safety Note
The `AIService` sanitizes the `error_message` string prior to persistence, ensuring the `GROQ_API_KEY` is redacted if it accidentally leaks into exception traces.
