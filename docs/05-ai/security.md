# AI & Evidence Security Model

## Ownership Boundaries
Users can only upload evidence to their own complaints. Trying to target another user's complaint yields a masked `404 Not Found` rather than `403 Forbidden` to prevent resource enumeration.
Similarly, retrieving evidence or AI results verifies that the underlying complaint belongs to the authenticated user.

## File Security
1. **Filename Sanitization:** The user's original filename is never used to construct the file path on disk. A generated UUID is used instead.
2. **MIME Verification:** Hardcoded allowed MIME types prevent execution of malicious code.
3. **Execution Prevention:** The backend serves as an API only. Files in the `uploads` directory are not served or executed as code.

## Secrets
- AI API keys are stored in backend environment variables only. They are completely inaccessible from the frontend.
- Error logs/records explicitly redact the configured `GROQ_API_KEY`.
