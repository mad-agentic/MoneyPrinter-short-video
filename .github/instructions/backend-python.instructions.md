---
applyTo: src/**/*.py
---
# Backend Python Instructions

## Scope
- Applies to Python code under src/.
- Keep edits small and behavior-preserving for existing automation flows.

## Required Patterns
- Config:
  - Use helpers from src/config.py (get_config and specialized getters).
  - Do not read config.json directly from feature code.
- LLM:
  - Use src/llm_provider.py as the only abstraction for model calls.
  - Avoid direct provider-specific API calls in business logic.
- Logging:
  - Use src/status.py for operational logs.
  - Keep messages concise because they are surfaced to the UI via SSE.
- Session data:
  - Preserve session-based state under .mp/sessions/<uuid>/.
  - Do not break resumable pipeline behavior.

## Structure Guidance
- Keep API route handling in src/api/*.py.
- Place heavy business logic in src/classes/*.py or shared modules in src/.
- Prefer adding focused helper functions over broad refactors.

## Safety Checklist
- Preserve current endpoint contracts and response shapes.
- When adding config keys, update config.example.json and config access paths.
- Keep cancellation/resume checks intact in long-running flows.
