# Copilot Instructions for MoneyPrinter

## Purpose
- Keep changes minimal, practical, and aligned with the current architecture.
- Preserve runtime behavior for automation flows (YouTube, Twitter, affiliate, outreach).
- Prefer linking to existing docs instead of duplicating long explanations.

## Quick Start Commands
- Setup (Windows):

```bat
setup.bat
```

- Run full web hub (backend + frontend):

```bat
start_hub.bat
```

- Backend only:

```bat
cd src
..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload
```

- Frontend only:

```bat
cd frontend
npm run dev -- --port 5174
```

- Frontend quality checks:

```bat
cd frontend
npm run lint
npm run build
```

## Architecture Snapshot
- Backend API routes: `src/api/`
- Core workflows: `src/classes/` (especially `YouTube.py`, `Twitter.py`)
- Shared backend utilities: `src/config.py`, `src/llm_provider.py`, `src/cache.py`, `src/status.py`
- Frontend app: `frontend/src/App.tsx` and `frontend/src/ResearchWorkspace.tsx`
- Runtime data: `.mp/` (auto-created), especially `.mp/sessions/`

## Project Conventions
- Config access:
  - Always use helpers from `src/config.py` (for example `get_config()` and specialized getters).
  - Do not read `config.json` directly from feature code.
- LLM usage:
  - Use `src/llm_provider.py` as the abstraction layer for Ollama/OpenAI-compatible calls.
  - Avoid direct provider-specific calls in business logic.
- Logging:
  - Use `src/status.py` for log output.
  - Keep logs clear; they are surfaced to the UI through SSE.
- Session pipeline:
  - Treat each video flow as session-based state under `.mp/sessions/<uuid>/`.
  - Preserve resumable behavior when adding/changing pipeline stages.
- API changes:
  - Keep route logic in `src/api/*.py`; avoid mixing route and heavy business logic.
  - Put business logic in `src/classes/*.py` or shared modules under `src/`.

## Common Pitfalls
- Missing environment setup:
  - If `venv` is missing, run `setup.bat` first.
- Port conflicts:
  - `start_hub.bat` frees ports `15001` and `5174`; avoid hardcoding alternate ports without reason.
- Selenium profile issues:
  - Ensure `firefox_profile` in `config.json` points to an existing, logged-in profile.
- ImageMagick path issues:
  - Verify `imagemagick_path` when subtitle composition fails.

## Change Guidance for Agents
- Prefer small, targeted edits over large refactors unless requested.
- Preserve public API behavior for existing frontend/backend interactions.
- When adding new settings, update both:
  - `config.example.json`
  - Any backend config getters/validation paths as needed.
- When adding endpoints, ensure UI integration expectations remain intact.

## Source References (Link, Do Not Duplicate)
- `README.md`
- `CLAUDE.md`
- `config.example.json`
- `scripts/preflight_local.py`

## Optional Next Step
- For this codebase size, consider adding scoped instruction files using `applyTo` patterns:
  - Backend Python: `src/**/*.py`
  - FastAPI layer: `src/api/**/*.py`
  - Frontend React/TS: `frontend/src/**/*.{ts,tsx}`

## Scoped Instructions Added
- `.github/instructions/backend-python.instructions.md`
- `.github/instructions/fastapi-api.instructions.md`
- `.github/instructions/frontend-react.instructions.md`
