# Authority Domain & State Machine

## Schema Boundaries
Authority configurations span three separate models structurally:
1. `Jurisdiction`: Defines geographic limits of governance organically.
2. `Department`: Operational branches actively processing issues (e.g., PWD vs Sanitation).
3. `AuthorityActionHistory`: Captures append-only immutable state events (Routing, Assignment, Transitioning).

## State Machine Constraints
Authority operations securely control progression through absolute limits preventing illogical domain jumps.
- A `SUBMITTED` complaint can only flow to `ASSIGNED`, `REJECTED`, or `INVALID`.
- An `ASSIGNED` complaint flows strictly to `IN_PROGRESS` or `REJECTED`.
- Only `IN_PROGRESS` actions map to `RESOLVED`.
- `RESOLVED` bounds logically link finally to `CLOSED` or permit a rollback sequence to `IN_PROGRESS` (Reopening).
Any unauthorized transition directly causes a `400 Bad Request` mapping.
