# Routing Engine & Assignment Workflow

The Routing Engine operates securely inside `RoutingService` without hallucinatory AI mapping biases.

## Execution Matrix
1. Engine receives the physical complaint `category` combined natively with an overriding `jurisdiction_id`.
2. Evaluates exactly mapped `RoutingRule` schemas stored in MongoDB.
3. Sorts deterministic boundaries by strict mathematical `priority` (ascending).
4. Emits `ambiguous` bounds proactively if competing rules conflict securely rather than guessing randomly.

## Auto-Assignment Output
If routing passes securely, `RoutingService` internally injects an exact database assignment schema into the `assignments` MongoDB collection, leaving the target `assigned_authority_id` explicitly blank. 
Individual personnel explicitly map into the assignment UUID dynamically during manual workflow progression via the Authority endpoints later.
