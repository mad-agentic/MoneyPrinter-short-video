# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MoneyPrinter is an automated short video creation and distribution platform. It generates YouTube Shorts (and other platforms) automatically using LLMs for scripting, Gemini for images, KittenTTS for voiceover, Whisper/AssemblyAI for subtitles, MoviePy for video composition, and Selenium for publishing.

## Commands

### Setup
```bash
setup.bat                # Windows: creates venv, installs Python deps + npm packages
scripts/setup_local.sh   # macOS/Linux equivalent
```

### Run
```bash
start_hub.bat      # Launches both backend (port 15001) and frontend (port 5174)

# Manual:
cd src && ..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload
cd frontend && npm run dev -- --port 5174
```

### CLI / Headless
```bash
python src/main.py                                    # Interactive CLI menu
python src/cron.py twitter <account_uuid> <model>    # Headless Twitter bot
python src/cron.py youtube <account_uuid> <model>    # Headless YouTube bot
python scripts/preflight_local.py                    # System dependency check
```

### Frontend
```bash
cd frontend && npm run build   # Production build
cd frontend && npm run lint    # Lint TypeScript
```

## Architecture

**Backend (FastAPI, port 15001):** `src/api/`
- `main.py` — app setup, `/system/*` endpoints (config, gallery, sessions, SSE logs)
- `youtube.py` — `/youtube/*` video generation & upload endpoints
- `twitter.py` — `/twitter/*` tweet management
- `affiliate.py` — `/affiliate/*` Amazon affiliate marketing
- `session_manager.py` — session CRUD (persisted under `.mp/sessions/`)
- `log_stream.py` — Server-Sent Events log streaming to UI
- `cancel_registry.py` — task cancellation

**Core Business Logic:** `src/classes/`
- `YouTube.py` (1,930 lines) — full pipeline: script → images → audio → subtitles → video → upload
- `Twitter.py` — tweet generation & Selenium posting
- `AFM.py` — Amazon scrape → pitch generation → affiliate tweet
- `Outreach.py` — Google Maps scraping → email outreach
- `Tts.py` — KittenTTS wrapper
- `PostBridge.py` — cross-posting to TikTok/Instagram

**Support Modules:** `src/`
- `llm_provider.py` — LLM abstraction (Ollama / OpenAI-compatible)
- `config.py` — reads `config.json` from project root
- `cache.py` — JSON persistence in `.mp/` directory
- `constants.py` — XPath/CSS selectors, menu constants
- `status.py` — colored terminal logging

**Frontend (React 19 + Vite, port 5174):** `frontend/src/`
- `App.tsx` (3,400+ lines) — monolithic UI: YouTube generator, Twitter manager, affiliate dashboard, gallery, config editor, real-time logs

## Configuration

Copy `config.example.json` → `config.json` and fill in:
- `llm_backend`: `"ollama"` or `"openai_compatible"`
- `ollama_model` / `openai_base_url` + `openai_model`
- `nanobanana2_api_key`: Gemini API key (image generation)
- `tts_voice`: `Jasper` | `Luna` | `Milo` | `Ava` | `Emma`
- `stt_provider`: `"local_whisper"` or `"assembly_ai"`
- `firefox_profile`: Firefox profile name for Selenium automation
- `video_encode_crf`: 0–51 (lower = higher quality, larger file)

## Data Storage

All runtime data lives in `.mp/` (auto-created):
- `youtube.json`, `twitter.json`, `afm.json` — account/product caches
- `sessions/<uuid>/` — per-video session files (script, images, audio, subtitles, final video)

## Key Patterns

- **Session-based pipeline:** Each video generation creates a UUID session. Progress is tracked by files present in the session directory. The API can resume interrupted sessions.
- **LLM abstraction:** Always use `src/llm_provider.py` functions rather than calling Ollama/OpenAI directly.
- **Config access:** Use `from config import get_config` — never read `config.json` directly.
- **Logging:** Use `src/status.py` for colored output; logs are also streamed to frontend via SSE.
- **Cancellation:** Long-running tasks register with `cancel_registry.py`; check `is_cancelled()` in loops.

## External Dependencies

| Service | Used For | Config Key |
|---------|----------|-----------|
| Ollama / OpenAI-compatible | Script & content generation | `llm_backend` |
| Google Gemini | Image generation | `nanobanana2_api_key` |
| KittenTTS | Text-to-speech voiceover | `tts_voice` |
| Whisper (local) or AssemblyAI | Speech-to-text subtitles | `stt_provider` |
| Firefox + Selenium | YouTube/Twitter publishing | `firefox_profile` |
| ImageMagick 7.x | Subtitle rendering overlay | `imagemagick_path` |
