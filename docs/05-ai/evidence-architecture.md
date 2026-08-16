# Evidence Architecture

## Upload Flow
1. Citizen triggers `POST /api/v1/complaints/{id}/evidence`.
2. Backend verifies ownership.
3. Backend validates MIME type (supported: `.jpg`, `.png`, `.webp`, `.pdf`).
4. Backend checks file size limits (default 10MB).
5. A unique UUID is generated to prevent path traversal, and the file is saved to `uploads/{complaint_id}/{uuid}.ext`.
6. An `EvidenceDocument` is created in MongoDB tracking the metadata.
7. The parent `ComplaintDocument.evidence_count` is incremented.

## Storage
- **Development/MVP:** Local filesystem (`uploads/` directory relative to backend).
- **Future Phases:** Can be mapped to an S3 bucket or Cloudinary service. The `storage_key` saved in the database abstracts the physical path.

## Retrieval
Retrieval endpoints (`GET /api/v1/complaints/{id}/evidence`) return ONLY metadata, hiding internal system storage paths to prevent unauthorized access.
