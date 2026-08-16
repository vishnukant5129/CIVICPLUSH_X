# CivicPulse AI — Citizen Complaint Domain

## Overview

Phase 4 establishes the core citizen complaint lifecycle for CivicPulse AI. It allows authenticated citizens to report civic issues, stores them securely in MongoDB, and restricts access strictly by ownership.

## Key Features

- **Complaint Creation:** Users can submit issues with categories, descriptions, and geographic locations.
- **Strict Ownership:** Complaints are securely bound to the authenticated citizen. Users can only view and list their own complaints.
- **Server-Controlled State:** The backend forcefully derives ownership from the session cookie, prevents injection of internal fields, and automatically initializes statuses (to `SUBMITTED`) and tracking timestamps.
- **Status Tracking:** The creation of a complaint atomically generates an immutable initial `StatusHistory` record.

## Quick Links

- [Domain Model](./domain-model.md)
- [API Contract](./api-contract.md)
- [Security Model](./security.md)
- [Testing Strategy](./testing.md)
