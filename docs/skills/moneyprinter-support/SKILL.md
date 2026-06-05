---
name: moneyprinter-support
description: Use when working inside the MoneyPrinter Short Video repository: understanding architecture, editing backend/frontend code, running local commands, handling sessions, config, logs, TTS/STT/video pipeline, and packaging repo skills.
argument-hint: "fix youtube generation bug, add API endpoint, package skills, debug TTS, update frontend"
allowed-tools: Bash, Read, Write, Edit, Grep
user-invocable: true
---

# MoneyPrinter Repository Support

Use this skill when the task is about this repository: MoneyPrinter Short Video.

MoneyPrinter is a local short-video automation app. It has a Python/FastAPI backend, a React/Vite frontend, session-based YouTube video generation, LLM scripting, Gemini image generation, TTS voiceover, STT subtitles, MoviePy composition, Selenium publishing, research chat, Twitter/X automation, affiliate marketing, outreach, and optional social cross-posting.

## First Read

Before editing, inspect the relevant files instead of guessing.

Start with:

- `README.md` for user-facing features and commands.
- `CLAUDE.md` for repository architecture and conventions.
- `config.example.json` for configurable behavior.
- `src/api/` for FastAPI routers.
- `src/classes/` for core automation classes.
- `frontend/src/` for React UI.

Use `rg` or `rg --files` first when searching.

## Project Map

- `src/api/main.py`: FastAPI app setup and system endpoints.
- `src/api/youtube.py`: YouTube generation, preview, publish, regenerate, and session endpoints.
- `src/api/research.py`: research chat sessions, SSE streaming, saved ideas.
- `src/api/session_manager.py`: session CRUD and persisted video state under `.mp/sessions/`.
- `src/api/log_stream.py`: Server-Sent Events logs for the UI.
- `src/api/cancel_registry.py`: cancellation flags for long-running work.
- `src/research_engine.py`: web search aggregation and LLM synthesis for content ideas.
- `src/llm_provider.py`: LLM abstraction for Ollama and OpenAI-compatible backends.
- `src/config.py`: config loading from project root.
- `src/cache.py`: JSON cache persistence in `.mp/`.
- `src/classes/YouTube.py`: main YouTube Shorts pipeline.
- `src/classes/Tts.py`: TTS runtime wrapper and fallback behavior.
- `src/classes/Twitter.py`: Twitter/X generation and Selenium posting.
- `src/classes/AFM.py`: Amazon affiliate marketing flow.
- `src/classes/Outreach.py`: local business scraping and email outreach.
- `frontend/src/App.tsx`: main React UI.
- `frontend/src/ResearchWorkspace.tsx`: research workspace UI.
- `docs/skills/`: repo-maintained skills and generated `.skill` packages.

## Commands

Setup:

```powershell
setup.bat
python scripts/preflight_local.py
```

Run both backend and frontend:

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

Frontend checks:

```powershell
cd frontend
npm run build
npm run lint
```

CLI/headless:

```powershell
python src/main.py
python src/cron.py twitter <account_uuid> <model>
python src/cron.py youtube <account_uuid> <model>
```

Package repo skills:

```powershell
python scripts/package_skills.py
python scripts/package_skills.py --skill moneyprinter-support
```

## Safe Edit Rules

- Keep changes scoped to the requested workflow.
- Do not refactor unrelated monolithic files just because they are large.
- Do not overwrite user changes in a dirty worktree.
- Do not commit `.mp/` runtime data, generated media, browser profiles, API keys, or local secrets.
- Treat `config.json` and `.env` as sensitive local files.
- Prefer existing helpers and patterns over new abstractions.
- For long-running features, preserve cancellation and UI log behavior.

## Backend Rules

- Use `src/llm_provider.py` for all LLM calls. Do not call Ollama or OpenAI-compatible APIs directly from new feature code.
- Use `from config import get_config` or existing config helpers. Do not manually parse `config.json` in feature code.
- Use `api.log_stream.add_log` for user-visible progress in web workflows.
- Use `api.cancel_registry` for cancellable loops or long-running jobs.
- Run blocking LLM/search/media work in a worker thread when inside async FastAPI streaming routes.
- Keep request models explicit with Pydantic `BaseModel`.
- Store runtime state under `.mp/` using existing session/cache helpers.

## Session And Pipeline Rules

MoneyPrinter uses UUID sessions. Each video session stores stage outputs so interrupted runs can resume.

When editing YouTube generation:

- Preserve `resume_session_id`, `force_new_session`, and `regenerate_from_step` semantics.
- Save stage data through `SessionManager.save_stage()` where possible.
- Keep script text TTS-ready. Stage directions, labels, markdown, and B-roll annotations must not be spoken.
- Respect `enable_cc`, `english_cc_bottom`, `tts_voice`, `script_language`, and publish mode fields.
- Keep manual review mode from auto-uploading.
- Avoid deleting session files unless explicitly requested.

## Frontend Rules

- Match existing React/Vite patterns in `frontend/src/`.
- Keep API base behavior consistent with current code.
- Preserve SSE log streaming and research chat streaming behavior.
- Avoid broad redesign unless the user asks.
- If changing UI, verify with `npm run build` and, when relevant, browser screenshots.

## Research Workflow Rules

The research feature stores sessions under `.mp/research/` and has modes:

- `chat`: normal LLM reply using conversation history.
- `research`: aggregate web search, synthesize insights.
- `ideas`: generate five structured short-video ideas.

When editing research:

- Preserve JSON idea shape used by the frontend.
- Keep generated `script_outline` as spoken text, not markdown or labeled sections.
- Clearly separate research text from saved idea data.

## Config And Secrets

Important config keys include:

- `llm_backend`, `ollama_base_url`, `ollama_model`
- `openai_base_url`, `openai_model`, `openai_api_key`
- `nanobanana2_api_key`, `nanobanana2_model`, `nanobanana2_aspect_ratio`
- `tts_engine`, `tts_fallback_engine`, `tts_voice`, `tts_language`
- `stt_provider`, `whisper_model`, `assembly_ai_api_key`
- `firefox_profile`, `headless`
- `imagemagick_path`, `video_encode_preset`, `video_encode_crf`
- `post_bridge`

Never print secret values in logs or final responses.

## Common Playbooks

### Debug YouTube Generation

1. Inspect `src/api/youtube.py` request flow.
2. Inspect `src/classes/YouTube.py` stage handling.
3. Check session metadata under `.mp/sessions/<id>/` only if needed and do not commit it.
4. Confirm logs use `add_log`.
5. Verify with the narrowest runnable command.

### Add Backend Endpoint

1. Add or update Pydantic request/response models in the relevant router.
2. Use existing helpers for config, cache, sessions, logging, and cancellation.
3. Register route under the existing router prefix.
4. Keep blocking work out of the event loop.

### Update Frontend Workflow

1. Find existing state and API helper patterns in `frontend/src/App.tsx` or `ResearchWorkspace.tsx`.
2. Keep request fields aligned with backend Pydantic models.
3. Preserve loading, error, cancel, and log states.
4. Run `npm run build`.

### Package Skills

1. Edit source under `docs/skills/<skill-name>/`.
2. Run `python scripts/package_skills.py --skill <skill-name>`.
3. Inspect generated archive contents if packaging behavior changed.

## Verification Checklist

Choose checks based on touched files:

- Skill/docs only: `python scripts/package_skills.py` and archive inspection.
- Packager changes: `python -m py_compile scripts/package_skills.py` plus package all and package one skill.
- Frontend changes: `cd frontend && npm run build`; run lint when TypeScript style changed.
- Backend changes: run targeted import/compile checks or the relevant API manually.
- Pipeline changes: verify session state, logs, cancellation, and manual review behavior.

Report which checks ran and which checks could not run.
