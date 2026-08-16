# CivicPulse AI — Master Plan

## 1. Project Identity

**Project:** CivicPulse AI  
**Category:** AI-powered Civic Problem Intelligence Platform  
**Primary goal:** Convert citizen-reported civic problems into structured, prioritized, geographically intelligent incidents that authorities can act on.

## 2. Vision

CivicPulse AI is not only a complaint-registration portal. It is an intelligence layer between citizens and civic authorities.

The system should:
1. Capture civic problems from citizens.
2. Understand the problem using AI.
3. Validate and structure the submitted information.
4. Detect duplicate/related complaints.
5. Group geographically related incidents.
6. Calculate severity and priority.
7. Recommend the responsible department and action.
8. Give authorities a live operational dashboard.
9. Learn from historical incidents to identify recurring hotspots and future risk.

## 3. Core Users

### Citizen
- Register/login.
- Submit a civic complaint.
- Upload evidence.
- Provide/select location.
- Track complaint status.
- Receive status updates.

### Civic Authority / Department
- View incoming complaints.
- Filter by status, category, severity, priority and location.
- Inspect evidence and AI analysis.
- View clusters and hotspots.
- Assign/route incidents.
- Update status.
- Monitor analytics and predictive insights.

### Administrator
- Manage departments/users.
- Manage categories and system configuration.
- Review audit information.
- Monitor system health and usage.

## 4. Core Product Loop

```text
Citizen Report
    ↓
Validation
    ↓
AI Understanding
    ↓
Geo + Duplicate Analysis
    ↓
Incident/Cluster Formation
    ↓
Severity + Priority
    ↓
Department Routing
    ↓
Authority Action
    ↓
Status Updates
    ↓
Historical Data
    ↓
Predictive Intelligence
```

## 5. MVP Scope

The MVP must prioritize a complete end-to-end working loop over a large number of disconnected features.

### Must Have
- Authentication and role-based access.
- Citizen complaint submission.
- Image/evidence upload.
- Location capture.
- Complaint categorization.
- AI-assisted complaint analysis.
- Duplicate/related complaint detection.
- Geographic clustering.
- Severity/priority scoring.
- Government/admin dashboard.
- Complaint assignment and status workflow.
- Complaint detail page.
- Basic analytics.
- Real-time status updates where technically justified.
- Audit trail for important state changes.

### Should Have
- Predictive hotspot analysis.
- AI-generated action recommendations.
- Department-level analytics.
- Notification system.
- Vector similarity search.

### Future / Post-MVP
- Direct integrations with municipal systems.
- Automated departmental ticket creation.
- WhatsApp/SMS ingestion.
- Multi-city deployment.
- Advanced forecasting.
- Mobile native applications.
- Citizen reputation/anti-abuse scoring.
- Cross-city benchmarking.

## 6. Architecture Direction

Initial architecture direction:

- Frontend: React-based web application.
- Backend: FastAPI modular monolith.
- Primary database: MongoDB Atlas.
- Geospatial indexing: MongoDB `2dsphere`.
- Semantic similarity: MongoDB Vector Search if validated during implementation.
- Background processing: Redis + RQ where asynchronous work is actually required.
- AI orchestration: LangGraph for multi-step reasoning workflows where justified.
- LLM provider: Groq as primary where appropriate; local Ollama only where resource/deployment constraints permit.
- Real-time communication: FastAPI WebSocket where live updates provide meaningful UX value.

**Important:** Architecture documentation must describe implemented/validated behavior. A technology must not be shown as implemented merely because it is planned.

## 7. Architectural Principles

1. Modular monolith first.
2. Keep the request path simple.
3. Use asynchronous workers only for genuinely long-running jobs.
4. Keep deterministic business rules separate from probabilistic AI.
5. AI must produce structured outputs.
6. Human/authority decisions remain authoritative for operational actions.
7. Store AI reasoning/results needed for auditability without exposing hidden chain-of-thought.
8. Design APIs before frontend/backend integration.
9. Validate all external inputs.
10. Avoid unnecessary microservices during MVP.

## 8. AI Responsibility Boundary

AI may:
- classify complaints,
- extract structured information,
- estimate severity,
- identify semantic similarity,
- recommend priority,
- recommend routing,
- summarize evidence,
- detect patterns.

AI must not silently:
- mark a complaint as resolved,
- falsely claim government action,
- fabricate evidence,
- fabricate official communications,
- override authorized human decisions.

## 9. Data Flow

```text
Citizen UI
   ↓
FastAPI API
   ↓
Validation
   ↓
Complaint Service
   ├── Database persistence
   ├── Evidence processing
   ├── AI analysis
   ├── Geo analysis
   └── Priority/routing
   ↓
Complaint + AI Analysis + Cluster
   ↓
Authority Dashboard
   ↓
Assignment / Status Update
   ↓
Citizen Notification
```

## 10. Major Domain Objects

- User
- Role
- Department
- Complaint
- Evidence
- Location
- Incident Cluster
- AI Analysis
- Assignment
- Status History
- Notification
- Prediction
- Audit Log

## 11. Status Lifecycle

Initial proposal:

```text
SUBMITTED
   ↓
UNDER_REVIEW
   ↓
VERIFIED
   ↓
ASSIGNED
   ↓
IN_PROGRESS
   ↓
RESOLVED
   ↓
CLOSED
```

Possible alternate outcomes:

```text
REJECTED
DUPLICATE
INVALID
```

Exact transition rules will be finalized in the complaint workflow specification.

## 12. Non-Functional Targets

The system should aim for:

- predictable API behavior,
- strong input validation,
- observable failures,
- secure authentication,
- role-based authorization,
- idempotent operations where appropriate,
- responsive dashboard interactions,
- traceable complaint state changes,
- graceful AI failure/fallback behavior.

Exact performance targets will be established after baseline testing.

## 13. Development Rule

No feature is considered complete until:

```text
PLANNED
→ DESIGNED
→ IMPLEMENTED
→ TESTED
→ VERIFIED
```

## 14. Documentation Rule

Design decisions must be documented before implementation when they affect:
- architecture,
- database schema,
- API contracts,
- authentication,
- AI behavior,
- background jobs,
- deployment.

## 15. Current Planning Status

- Product concept: Defined
- Core value proposition: Defined
- Initial architecture direction: Defined
- MVP boundary: Defined
- Detailed database design: Pending
- Detailed API contract: Pending
- Detailed AI pipelines: Pending
- UI/UX specification: Pending
- Security model: Pending
- Test strategy: Pending
- Deployment design: Pending

## 16. Definition of Done for Planning

Planning is complete only when:
- MVP features are frozen.
- Architecture is internally consistent.
- Database schema is defined.
- API contracts are defined.
- AI pipelines have explicit inputs/outputs/failure behavior.
- Frontend pages and states are defined.
- Security requirements are defined.
- Testing strategy exists.
- Implementation phases have dependencies and acceptance criteria.
