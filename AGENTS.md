# AGENTS.md

Guidance for Codex and other coding agents working in this repository.

## Project Shape

MoneyPrinter Short Video is a local automation app for short-video creation and distribution. It uses Python/FastAPI for backend workflows, React/Vite for the web UI, and local/runtime state under `.mp/`.

Main areas:

- `src/api/`: FastAPI endpoints, SSE logs, session APIs, cancel registry.
- `src/classes/`: long-running workflow implementations for YouTube, Twitter/X, affiliate, outreach, TTS, and posting.
- `src/providers/`: provider adapters and schemas for external AI/media services.
- `src/classes/Tts.py`: TTS engine selection, voice handling, warm-up, synthesis, and fallback behavior.
- `src/research_engine.py`: Research & Ideas search aggregation and LLM synthesis.
- `src/llm_provider.py`: shared LLM access. Use this instead of direct Ollama/OpenAI calls.
- `src/config.py`: shared config access. Use `get_config()` instead of opening `config.json` directly.
- `frontend/src/`: React UI. `App.tsx` is the main dashboard; `ResearchWorkspace.tsx` owns Research & Ideas UI.
- `docs/skills/`: source skills and generated `.skill` archives.
- `.mp/`: runtime data only. Do not commit or treat as source.

## Commands

Setup:

```powershell
setup.bat
```

Run full app on Windows:

```powershell
start_hub.bat
```

Run backend manually:

```powershell
cd src
..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload
```

Run frontend manually:

```powershell
cd frontend
npm run dev -- --port 5174
```

Useful checks:

```powershell
python scripts\preflight_local.py
python -m py_compile src\config.py src\llm_provider.py src\research_engine.py
cd frontend; npm run lint; npm run build
python scripts\package_skills.py
```

Use focused checks for touched files. Run frontend checks only when frontend files change. Run `python scripts\package_skills.py --skill <name>` when editing one skill.

## Routing Rules

Use these paths first:

- YouTube generation, resume, upload, subtitles, video composition: `src/classes/YouTube.py`, `src/api/youtube.py`.
- Twitter/X posting and accounts: `src/classes/Twitter.py`, `src/api/twitter.py`.
- TTS and audio synthesis: `src/classes/Tts.py`, provider files under `src/providers/`.
- TTS voice/model settings and UI fields: `src/config.py`, `config.example.json`, `src/api/main.py`, `src/api/youtube.py`, `src/classes/Tts.py`, `frontend/src/App.tsx`.
- Research & Ideas backend: `src/research_engine.py`, `src/api/research.py`.
- Research & Ideas frontend: `frontend/src/ResearchWorkspace.tsx`.
- Main dashboard, settings, gallery, sessions, logs: `frontend/src/App.tsx`, `src/api/main.py`, `src/api/session_manager.py`, `src/api/log_stream.py`.
- LLM model behavior and provider routing: `src/llm_provider.py`, `src/providers/`.
- Skill source/package work: `docs/skills/`, `scripts/package_skills.py`.

## Coding Rules

- Prefer existing patterns over new abstractions.
- Keep edits scoped to requested behavior.
- Do not rewrite large files unless needed for the task.
- Do not call provider APIs directly from feature code; route through existing provider or LLM modules.
- Do not read or write `config.json` directly in business logic; use `src/config.py` helpers.
- For TTS voice changes, keep `tts_model`, `tts_voice`, `tts_response_format`, `tts_engine`, `tts_fallback_engine`, `tts_language`, and `tts_sample_rate` behavior consistent across config helpers, API payloads, frontend settings, and `TTS` constructor usage.
- Long-running flows should log through existing status/log-stream patterns and respect cancellation when possible.
- Session data should remain under `.mp/sessions/<uuid>/`.
- Keep user-visible generated scripts free of stage directions that should not be spoken by TTS.
- When editing skills, update source folder and regenerate matching `.skill` archive.

## Data And Secrets

Never commit or package:

- `.env`
- `config.json`
- `.mp/`
- browser profiles, cookies, tokens, local account caches
- generated media outputs
- `venv/`, `frontend/node_modules/`, build/cache folders

Use `config.example.json` for documented defaults and examples.

## Git Hygiene

The worktree may contain user changes. Do not revert, overwrite, or clean files you did not touch unless the user explicitly asks.

Before editing, inspect relevant files. Before final response, report:

- files changed by this task
- verification commands run
- commands that could not run and why

## Verification Guide

For backend Python edits:

```powershell
python -m py_compile <touched-python-files>
```

For API or workflow edits, also smoke-check imports where practical:

```powershell
python -m py_compile src\api\main.py src\api\youtube.py src\classes\YouTube.py
```

For frontend edits:

```powershell
cd frontend
npm run lint
npm run build
```

For skills:

```powershell
python scripts\package_skills.py --skill <skill-name>
```

For config/provider changes, check both config and caller modules:

```powershell
python -m py_compile src\config.py src\llm_provider.py src\providers\__init__.py src\providers\registry.py
```

For TTS or voice changes, check config, API, and synthesis modules together:

```powershell
python -m py_compile src\config.py src\api\main.py src\api\youtube.py src\classes\Tts.py src\classes\YouTube.py
```

## Notes For Codex

- Prefer `rg` for search.
- Use `apply_patch` for manual file edits.
- Keep final answers concise and include concrete file paths.
- If a local dev server is needed for UI verification, start it and provide the URL.
- If `refs/` appears again, treat it as disposable reference material unless code explicitly reads it.
