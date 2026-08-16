# CivicPulse AI — Dashboard & Analytics

## Overview

Phase 6 implements the first operational citizen dashboard for CivicPulse AI, built entirely on actual, persisted MongoDB data. It adheres to the absolute global rule: **ZERO FAKE DATA**.

## Key Features

- **Dashboard Summary:** Aggregates total complaints, categorizes them by status and category, tracks trend data over time, and computes evidence/AI processing metrics.
- **Geographic Visualization:** Integrates React Leaflet to map actual complaint coordinates on an interactive map. If a complaint lacks coordinates, it is gracefully ignored.
- **MongoDB Aggregation:** Utilizes the `$facet` operator to execute parallel pipelines in a single database round-trip, optimizing performance.
- **Filtering:** Citizens can filter their dashboard view by `status`, `category`, and time range (date bounds).
- **Security & Data Isolation:** All dashboard data is scoped explicitly to the authenticated citizen. Cross-user data leakage is structurally impossible.

## Quick Links

- [Dashboard Architecture](./dashboard-architecture.md)
- [Analytics Model](./analytics-model.md)
- [Dashboard API](./dashboard-api.md)
- [Geographic Visualization](./geographic-visualization.md)
- [Background Processing](./background-processing.md)
- [Security Model](./security.md)
- [Testing Strategy](./testing.md)
