# 9Router Provider Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a provider layer so 9Router can power chat, image generation, TTS, STT, and research search while keeping old providers as fallback.

**Architecture:** Add a focused `src/providers/` package with schemas, registry helpers, and a 9Router client. Wire existing pipeline entry points to try 9Router first when active, then fallback to current local/Gemini/Whisper/Kitten behavior. Extend Settings UI and config save/load for nested 9Router config.

**Tech Stack:** Python 3.12, `requests`, FastAPI, React 19/Vite, existing MoviePy/TTS/STT pipeline.

---

## File Structure

- Create `src/providers/__init__.py`: package marker.
- Create `src/providers/schemas.py`: dataclasses for generated files and search results.
- Create `src/providers/ninerouter.py`: 9Router HTTP client.
- Create `src/providers/registry.py`: config-driven activation and provider access.
- Modify `src/config.py`: add getters for `ai_provider` and `providers.ninerouter`.
- Modify `src/llm_provider.py`: sync chat model from 9Router config when active.
- Modify `src/classes/YouTube.py`: try 9Router image generation and STT.
- Modify `src/classes/Tts.py`: try 9Router TTS before local engines.
- Modify `src/research_engine.py`: try 9Router search before DuckDuckGo.
- Modify `src/api/main.py`: allow nested config and add model endpoints.
- Modify `frontend/src/App.tsx`: add 9Router Settings card and save fields.
- Modify `config.example.json`: add provider defaults.

## Tasks

### Task 1: Config Helpers

- [ ] Add `get_ai_provider_config()`, `get_provider_configs()`, and `get_ninerouter_config()` to `src/config.py`.
- [ ] Defaults must preserve current behavior when keys are missing.
- [ ] Add matching defaults to `config.example.json`.

### Task 2: 9Router Provider Package

- [ ] Add `src/providers/schemas.py` dataclasses: `GeneratedFile`, `SearchResult`.
- [ ] Add `src/providers/ninerouter.py` with methods: `list_chat_models`, `list_image_models`, `chat_completion`, `generate_image`, `synthesize_speech`, `transcribe_audio`, `search`.
- [ ] Add `src/providers/registry.py` with `is_ninerouter_active()`, `fallback_to_local()`, `get_ninerouter()`.
- [ ] Keep API keys masked in errors/logs.

### Task 3: Text Compatibility

- [ ] Update `src/llm_provider.py` so when 9Router is active, text model comes from `providers.ninerouter.chat_model`, with existing `openai_model` fallback.
- [ ] Keep current OpenAI-compatible behavior for non-9Router routers.

### Task 4: Image Provider Wiring

- [ ] In `src/classes/YouTube.py`, before current Nano Banana/Gemini call, try 9Router image generation when active.
- [ ] Save image bytes to the same session image output path style current pipeline expects.
- [ ] If 9Router fails and fallback is enabled, log warning and continue to current Gemini path.

### Task 5: TTS Provider Wiring

- [ ] In `src/classes/Tts.py`, support engine value `ninerouter`.
- [ ] When active, synthesize speech with 9Router into an audio file and return path compatible with current callers.
- [ ] If 9Router fails and fallback is enabled, continue to Kitten/OmniVoice fallback.

### Task 6: STT Provider Wiring

- [ ] In `src/classes/YouTube.py`, add 9Router transcription branch when active.
- [ ] Prefer `srt` response format so current subtitle flow can reuse output.
- [ ] If 9Router fails and fallback is enabled, continue current local Whisper/AssemblyAI path.

### Task 7: Search Provider Wiring

- [ ] In `src/research_engine.py`, try 9Router search when active.
- [ ] Normalize search output to existing `{title, url, body, published}` dicts.
- [ ] If 9Router fails and fallback is enabled, use current DuckDuckGo flow.

### Task 8: Backend Config API

- [ ] Allow `ai_provider` and `providers` in `EDITABLE_CONFIG_KEYS` in `src/api/main.py`.
- [ ] Add `GET /system/ai/models/chat` and `GET /system/ai/models/image` endpoints.
- [ ] Preserve existing `/system/llm/models` endpoint.

### Task 9: Settings UI

- [ ] Extend `ConfigWorkspace` state with `ai_provider` and `providers.ninerouter` defaults.
- [ ] When `llm_backend` is `openai_compatible`, show a 9Router Media & Search card.
- [ ] Save nested config through `/system/config`.
- [ ] Add image model fetch using `/system/ai/models/image`.
- [ ] Keep current LLM model fetch behavior.

### Task 10: Verification

- [ ] Run Python compile check:

```powershell
python -m py_compile src\providers\__init__.py src\providers\schemas.py src\providers\ninerouter.py src\providers\registry.py src\config.py src\llm_provider.py src\classes\Tts.py src\classes\YouTube.py src\research_engine.py src\api\main.py
```

- [ ] Run frontend build:

```powershell
cd frontend
npm run build
```

- [ ] Run package skills only if previous skill work is still pending:

```powershell
python scripts/package_skills.py
```

- [ ] Report any checks not run.
