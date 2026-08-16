# CivicPulse AI — MVP Scope

## 1. Objective

Build the smallest complete version of CivicPulse AI that proves the core intelligence loop rather than attempting every possible feature.

## 2. MVP Golden Path

```text
Citizen Login
   ↓
Report Civic Problem
   ↓
Upload Evidence + Location
   ↓
AI Classification
   ↓
Duplicate / Related Detection
   ↓
Priority Calculation
   ↓
Authority Dashboard
   ↓
Assignment
   ↓
Status Update
   ↓
Citizen Sees Update
```

## 3. MVP Modules

### A. Authentication
- Registration/login
- Citizen role
- Authority role
- Admin role if required for configuration

### B. Citizen Complaint
- Complaint form
- Category
- Description
- Location
- Evidence upload
- Submission confirmation
- Complaint tracking

### C. AI Intelligence
- Category classification
- Structured extraction
- Evidence analysis where supported
- Semantic duplicate/related detection
- Priority score
- Department recommendation

### D. Geo Intelligence
- Store coordinates
- Geographic index
- Nearby complaint retrieval
- Basic incident clustering
- Map visualization

### E. Authority Operations
- Dashboard
- Complaint queue
- Filters
- Complaint detail
- AI analysis
- Assignment
- Status updates

### F. Analytics
- Total complaints
- Open/resolved counts
- Category distribution
- Priority distribution
- Map/cluster visualization

### G. Real-Time
Implement only if required by the chosen UX:
- authority status update,
- citizen status refresh/update,
- live dashboard changes.

## 4. MVP Data Objects

Minimum required:

```text
User
Complaint
Evidence
Department
AIAnalysis
IncidentCluster
Assignment
StatusHistory
```

Optional for first implementation:

```text
Notification
Prediction
AuditLog
```

These become mandatory if the corresponding feature is implemented.

## 5. MVP AI Pipeline

```text
Input
 ↓
Validation
 ↓
Classification
 ↓
Structured Extraction
 ↓
Similarity Search
 ↓
Geo-Proximity Check
 ↓
Cluster Decision
 ↓
Priority Score
 ↓
Department Recommendation
 ↓
Persist Result
```

## 6. Priority Model

The initial implementation should use an explicit scoring model rather than allowing an LLM to invent priority.

Example structure:

```text
priority =
    severity_weight
  + evidence_confidence_weight
  + related_report_weight
  + location_factor
  + duration_factor
```

Exact weights must be defined and tested before production/demo use.

## 7. MVP Predictive Layer

Predictive intelligence is **secondary to the core complaint workflow**.

First implementation may provide:
- historical complaint density,
- category/time trends,
- recurring hotspots.

Advanced forecasting should only be implemented after sufficient historical/synthetic data exists.

## 8. Demo Dataset

Because a real municipal data integration is not guaranteed, the MVP should support a controlled synthetic/demo dataset.

The dataset should contain:
- realistic complaint descriptions,
- categories,
- coordinates,
- timestamps,
- statuses,
- repeated reports around selected hotspots.

This allows clustering and analytics to be demonstrated honestly.

## 9. MVP Definition of Done

The MVP is complete when:

- [ ] Citizen can authenticate.
- [ ] Citizen can submit a complaint.
- [ ] Complaint is persisted.
- [ ] Evidence can be attached.
- [ ] Location is persisted.
- [ ] AI analysis produces structured output.
- [ ] Related complaints can be detected.
- [ ] Priority is calculated.
- [ ] Authority can see the complaint.
- [ ] Authority can assign/update it.
- [ ] Status history is recorded.
- [ ] Citizen can see the updated status.
- [ ] Dashboard provides basic analytics.
- [ ] At least one geographic hotspot/cluster can be demonstrated.
- [ ] Failure cases are handled.
- [ ] Core flow has integration tests.

## 10. Explicitly Deferred

Do not implement these before the golden path works:

- multi-city federation,
- complex autonomous agents,
- unnecessary microservices,
- advanced forecasting,
- direct government integrations,
- native mobile applications,
- large-scale notification infrastructure,
- complicated gamification.

## 11. MVP Priority Order

### P0 — Must Work
Authentication → Complaint → Evidence → Location → Persistence → Authority Dashboard

### P1 — Intelligence
Classification → Duplicate Detection → Priority → Department Recommendation

### P2 — Civic Intelligence
Clustering → Analytics → Hotspots → Real-time updates

### P3 — Predictive
Historical patterns → Risk/forecasting → Preventive recommendations
