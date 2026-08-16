# CivicPulse AI — Evidence Intelligence & AI

## Overview

Phase 5 introduces the first intelligence layer to CivicPulse AI by allowing citizens to upload real evidence (images/documents) alongside their complaints, which automatically triggers asynchronous AI analysis using Groq to produce structured metadata.

## Key Features

- **Evidence Upload:** Citizens can upload files safely. Storage is currently mocked via the local `uploads/` directory for MVP, but the path logic is completely traversal-safe.
- **AI Integration:** Evidence upload automatically triggers an asynchronous call to the LLM (`AIService`).
- **Structured Output:** The LLM returns a strict JSON object validated against `AIAnalysisDocument`.
- **Fault Tolerance:** If the LLM call fails, the evidence and complaint remain safely preserved, and the AI Analysis record is marked as `FAILED`.
- **Ownership Security:** Users can only view or upload evidence for their own complaints.

## Quick Links

- [Evidence Architecture](./evidence-architecture.md)
- [AI Architecture](./ai-architecture.md)
- [Provider Configuration](./provider-configuration.md)
- [Failure Handling](./failure-handling.md)
- [Security Model](./security.md)
- [Testing Strategy](./testing.md)
