# 9Router Provider Layer Design

Date: 2026-06-05

## Goal

Build a real provider layer for MoneyPrinter so one selected AI provider can power text, image generation, TTS, STT, and research search. 9Router is the first full provider. Existing local/Gemini/Whisper/Kitten behavior remains as fallback so the video pipeline does not break.

## Scope

Phase 1 creates the provider foundation and wires 9Router into the highest-value paths:

- Text remains compatible through `src/llm_provider.py`.
- Image generation can use 9Router `/v1/images/generations` before falling back to current Nano Banana/Gemini code.
- TTS can use 9Router `/v1/audio/speech` before falling back to current Kitten/OmniVoice code.
- STT can use 9Router `/v1/audio/transcriptions` before falling back to current local Whisper/AssemblyAI code.
- Research search can use 9Router `/v1/search` before falling back to DuckDuckGo search.
- Settings UI exposes 9Router media/search config and saves it into `config.json`.

## Architecture

Create provider modules:

```text
src/providers/
  __init__.py
  schemas.py
  registry.py
  ninerouter.py
```

`schemas.py` contains small dataclasses for search results and generated media outputs.

`ninerouter.py` owns all 9Router HTTP calls:

- `GET /v1/models`
- `GET /v1/models/image`
- `POST /v1/chat/completions`
- `POST /v1/images/generations`
- `POST /v1/audio/speech`
- `POST /v1/audio/transcriptions`
- `POST /v1/search`

`registry.py` answers whether 9Router should be active and returns provider instances. It uses config, not hard-coded URLs.

Existing files become consumers:

- `src/llm_provider.py`: can remain the public compatibility wrapper for text.
- `src/classes/YouTube.py`: tries provider image/STT paths when 9Router is active.
- `src/classes/Tts.py`: tries 9Router TTS when configured, falls back to local engines.
- `src/research_engine.py`: tries 9Router search when configured, falls back to DuckDuckGo.

## Config

Add new config while keeping old keys:

```json
"ai_provider": {
  "active": "ninerouter",
  "fallback_to_local": true
},
"providers": {
  "ninerouter": {
    "enabled": true,
    "base_url": "http://localhost:20128",
    "api_key": "none",
    "chat_model": "cx/gpt-5.5",
    "image_model": "gemini/gemini-3-pro-image-preview",
    "image_size": "1024x1792",
    "tts_model": "edge-tts/vi-VN-HoaiMyNeural",
    "tts_voice": "vi-VN-HoaiMyNeural",
    "tts_response_format": "mp3",
    "stt_model": "openai/whisper-1",
    "stt_response_format": "srt",
    "search_model": "",
    "search_max_results": 10
  },
  "local": {
    "enabled": true
  }
}
```

Backward compatibility:

- Existing `llm_backend`, `openai_*`, `nanobanana2_*`, `tts_*`, `stt_provider`, and `whisper_*` keys remain valid.
- If `ai_provider.active` is missing, code follows the old behavior.
- When Settings saves OpenAI-compatible/9Router values, it syncs the new 9Router block from the existing LLM fields.

## Activation Rules

9Router is active when:

- `ai_provider.active == "ninerouter"`
- `providers.ninerouter.enabled == true`

The Settings UI sets those values automatically when the user selects `OpenAI-compatible (9router, ProxyAPI...)`.

If a 9Router capability fails and `ai_provider.fallback_to_local` is true, the pipeline logs a warning and uses the current local/Gemini provider.

## Settings UI

In `ConfigWorkspace`, keep the current LLM card. When `llm_backend === "openai_compatible"`, show a 9Router card with:

- Base URL
- API key
- Chat model
- Image model
- Image size
- TTS model
- TTS voice
- TTS response format
- STT model
- STT response format
- Search model
- Search max results
- Fallback to local toggle
- Fetch chat models button
- Fetch image models button

The existing Save button writes the new nested config through `/system/config`.

## API Changes

Allow nested config keys in `src/api/main.py`:

- `ai_provider`
- `providers`

Add optional endpoints:

- `GET /system/ai/models/chat`
- `GET /system/ai/models/image`

These call the provider registry. Existing `/system/llm/models` remains for compatibility.

## Error Handling

- 9Router HTTP failures include status code and short response text.
- Missing models raise actionable errors naming the config key.
- API keys are never printed.
- Generated binary files are written into existing session paths.
- Fallback logs should say which capability fell back, not include secrets.

## Verification

Minimum verification for phase 1:

- `python -m py_compile src/providers/*.py src/config.py src/llm_provider.py src/classes/Tts.py src/classes/YouTube.py src/research_engine.py src/api/main.py`
- `cd frontend && npm run build`
- Manual config load/save through Settings.
- Manual model fetch for chat and image where 9Router is running.

Runtime media verification can be done with one short manual video generation after config is set.

## Out Of Scope For Phase 1

- Removing old provider config keys.
- Full provider framework for every third-party API.
- Rewriting the whole YouTube pipeline.
- Installing or managing 9Router itself.
- Committing local secrets from `.env` or `config.json`.
