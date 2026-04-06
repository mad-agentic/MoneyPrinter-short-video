---
applyTo: src/api/**/*.py
---
# FastAPI API Layer Instructions

## Scope
- Applies only to FastAPI route modules in src/api/.

## API Boundary Rules
- Keep route/controller logic in src/api/*.py.
- Move heavy processing to src/classes/*.py or shared modules under src/.
- Maintain backwards compatibility for request/response payloads unless explicitly asked.

## Implementation Rules
- Reuse existing models, helpers, and patterns in sibling route files.
- Use src/status.py for logs that should appear in UI streams.
- Respect session lifecycle patterns from session_manager and .mp/sessions storage.
- Keep cancellation support intact for long-running operations.

## Change Discipline
- Prefer additive, minimal edits over large rewrites.
- If introducing new settings, wire them through config helpers instead of direct file reads.
- Ensure route registration expectations in src/api/main.py remain valid.

## Validation
- Verify that changed endpoints still align with frontend expectations in frontend/src/.
- If an endpoint contract changes by request, clearly update dependent UI usage in the same change.
