# Testing Strategy

## Mock Isolation
Since external AI calls cost money and introduce test latency, we mock `AsyncGroq` entirely within our test suite (`tests/test_evidence_ai.py`).

## Covered Scenarios
- **Upload Success:** Checks file parsing, size constraints, and valid DB insertions.
- **Trigger Alignment:** Ensures `ai_service.analyze_complaint` is fired asynchronously upon evidence upload.
- **AI Structured Output:** Validates that a successfully mocked JSON string from Groq is correctly decoded, domain validated, and updated within the `AIAnalysisRepository`.
