# MoneyPrinter Roadmap Stabilization Design

Date: 2026-06-06

## Goal

Bring MoneyPrinter Short Video back into alignment with its README workflow, remove the known 9Router configuration traps, and define an incremental roadmap for subtitle quality, deterministic rendering, content sourcing, and publishing safety.

This is a phased design. Phase 0 and Phase 1 are required before larger feature work because they fix active breakage and make the app easier to validate. Later phases are independent tracks that should be implemented one at a time with their own verification.

## Current Findings

The project already has the main product shape promised by the README: FastAPI backend, React/Vite dashboard, YouTube generation workflow, Research & Ideas, Twitter/X, affiliate, PostBridge cross-posting, local runtime state under `.mp/`, and Settings for provider configuration.

The main gaps are operational and consistency gaps:

- 9Router search still has stale `search-combo` defaults in the frontend and provider selection path, while current docs and config defaults use `tavily/search`.
- `README.md` and `readme_vn.md` still document 9Router `search-combo` for research.
- The local `config.json` can save chat models into STT/TTS fields. That causes errors like `Provider 'codex' does not support STT` or equivalent provider capability mismatches.
- Frontend lint fails on `no-explicit-any` in Settings config handling, even though `npm run build` passes.
- `scripts/preflight_local.py` checks only old local assumptions. It does not validate 9Router capability routing.
- Repository instructions say to use `get_config()` from `src/config.py`, but no public helper with that exact name exists there.
- Runtime docs do not clearly warn that `start_hub.bat` kills processes on ports `15001` and `5174`.
- README claims multi-platform publishing. Code supports this through Twitter/X and PostBridge, but docs should state that TikTok/Instagram need PostBridge config and are not enabled by default.

Verification already run during audit:

- `python -m json.tool config.example.json` passed.
- `python -m json.tool config.json` passed.
- `python -m py_compile src\config.py src\llm_provider.py src\research_engine.py src\providers\__init__.py src\providers\registry.py src\providers\ninerouter.py src\api\main.py src\api\youtube.py src\classes\Tts.py src\classes\YouTube.py` passed.
- `python scripts\preflight_local.py` failed because Ollama was unreachable, Firefox profile path was not a real path, and ImageMagick was not detected at the configured path.
- `cd frontend && npm run lint` failed with 18 `@typescript-eslint/no-explicit-any` errors in `frontend/src/App.tsx`.
- `cd frontend && npm run build` passed.

## Reference Direction

The requested reference projects inform the roadmap:

- VideoLingo: word-level subtitle recognition, subtitle segmentation, terminology handling, single-line subtitles, translation quality loop, and dubbing options.
- Remotion: programmatic video composition with React components.
- HyperFrames: deterministic HTML/CSS/media rendering to MP4 using headless browser capture and FFmpeg.
- MoneyPrinterV2: cron-oriented YouTube, Twitter/X, affiliate, and outreach modules.
- RedditVideoMakerBot: user-selectable source/background/music/voice choices and duplicate prevention.

MoneyPrinter should not copy these projects wholesale. It should use their strongest patterns where they fit the current local-first architecture.

## Scope

### Phase 0: Stabilize Current App

Fix active errors and doc drift without changing product architecture.

Required behavior:

- `tavily/search` is the default web search model everywhere.
- `search-combo` is never auto-selected ahead of `tavily/search`.
- Settings save preserves valid nested 9Router config without `any` typing.
- README, Vietnamese README, and usage docs describe the same default models.
- Local `config.json` should use valid TTS/STT model defaults when 9Router is active.
- Preflight should report provider capability problems clearly and mask API keys.

### Phase 1: Provider And Config Guardrails

Make provider configuration harder to break.

Required behavior:

- `src/config.py` exposes a public `get_config()` helper that returns a parsed config dict.
- Existing config getters use or remain compatible with that helper.
- 9Router model listing endpoints can be used to validate `chat_model`, `image_model`, `tts_model`, `stt_model`, and `search_model` by capability.
- Settings UI should warn when a selected model is missing from the capability list.
- Preflight should validate active provider settings and report actionable warnings without printing secrets.

### Phase 2: Subtitle And Dubbing Quality

Improve caption quality before adding new renderer complexity.

Required behavior:

- Subtitle generation supports stricter single-line caption formatting for short-form video.
- A glossary/terminology list can be passed into research/script/subtitle translation flows.
- Translation uses a three-step flow: translate, reflect, adapt.
- Word-level timing support can be added behind an optional provider path such as WhisperX without replacing local Whisper by default.
- Dubbing remains optional. Existing TTS behavior stays backward compatible.

### Phase 3: Deterministic Renderer Track

Add a second rendering engine without removing MoviePy.

Required behavior:

- Existing MoviePy compose path remains the default.
- A renderer abstraction lets sessions choose `moviepy` or `html`.
- The HTML renderer produces frame-stable 1080x1920 MP4 output from a local composition file.
- HTML renderer supports captions, image/video layers, music, title card, and simple motion presets.
- Verification includes a short render smoke test and artifact inspection.

### Phase 4: Content Engine Improvements

Improve research quality, asset choice, and duplicate prevention.

Required behavior:

- Research clearly labels source types: Web, YouTube, Reddit, TikTok.
- Users can choose or lock background music, background video/image style, voice, and format template.
- Sessions can detect duplicate subject/script hashes before generating another video.
- Research ideas hand off TTS-ready spoken scripts only, with no labels or stage directions.

### Phase 5: Publish And Schedule Safety

Make distribution explicit and auditable.

Required behavior:

- Manual review remains the default publish mode.
- Auto publish requires explicit config and visible UI state.
- TikTok/Instagram docs and UI state name PostBridge as the required integration.
- Scheduler/cron work is explicit per account and per platform.
- Publish attempts write clear session state for success, skipped, failed, and retryable states.

## Architecture

### Existing Modules To Preserve

- `src/api/youtube.py` remains the API entry point for YouTube generation, regenerate, cancel, manual review, and push-now.
- `src/classes/YouTube.py` remains the current generation workflow owner until renderer abstraction is introduced.
- `src/classes/Tts.py` remains the TTS engine owner.
- `src/research_engine.py` remains the Research & Ideas aggregation and synthesis owner.
- `src/providers/ninerouter.py` remains the 9Router HTTP client.
- `src/providers/registry.py` remains the provider activation layer.
- `src/config.py` remains the config access layer.
- `frontend/src/App.tsx` owns Settings and the main dashboard.
- `frontend/src/ResearchWorkspace.tsx` owns the Research & Ideas UI.

### New Boundaries

Provider validation should be a small boundary around 9Router configuration. It should not spread provider-specific HTTP calls across feature code. Feature code should ask the provider layer whether a model is valid for a capability.

Renderer abstraction should be introduced only when Phase 3 starts. It should define a narrow interface such as `compose(session, assets, audio, subtitles) -> video_path`. The MoviePy implementation can wrap existing `YouTube.combine()` behavior first.

Subtitle enhancement should live near subtitle generation and formatting. It should not be mixed into upload or account management code.

Content engine improvements should remain in Research & Ideas and session metadata. They should not mutate `.mp/` outside existing session managers.

## Data Flow

Current flow remains:

```text
Settings -> config.json -> config.py -> provider registry
Research -> research_engine.py -> llm_provider.py -> ideas
YouTube UI -> src/api/youtube.py -> YouTube workflow
YouTube workflow -> script -> metadata -> prompts -> images -> TTS -> STT -> compose -> review -> publish
Session state -> .mp/sessions/<id>/session.json
```

Phase 3 adds:

```text
YouTube workflow -> renderer selection -> MoviePy renderer or HTML renderer -> MP4
```

Phase 5 adds:

```text
Ready for review -> Push Now or Scheduler -> YouTube/Twitter/PostBridge -> publish state
```

## Error Handling

- Provider errors must include capability and model name, for example `9Router STT model invalid: cx/gpt-5.5 is not listed in /v1/models/stt`.
- API keys must be masked in logs and exception text.
- Fallback logs must say which capability fell back: search, image, TTS, STT, or chat.
- If fallback is disabled, provider failure should stop the stage and save session state as failed.
- If fallback is enabled, provider failure should continue only when a local fallback exists.
- Cancel should remain stage-boundary based until finer-grained cancellation is designed.

## Testing And Verification

Phase 0 and Phase 1 require:

```powershell
python -m json.tool config.example.json
python -m json.tool config.json
python -m py_compile src\config.py src\llm_provider.py src\research_engine.py src\providers\__init__.py src\providers\registry.py src\providers\ninerouter.py src\api\main.py src\api\youtube.py src\classes\Tts.py src\classes\YouTube.py
python scripts\preflight_local.py
cd frontend; npm run lint; npm run build
```

Phase 2 requires subtitle fixture tests and one local subtitle generation smoke test.

Phase 3 requires a renderer smoke test that creates a short MP4 and checks that output is non-empty, 1080x1920, and has audio.

Phase 4 requires Research & Ideas smoke tests for source labeling and duplicate detection.

Phase 5 requires publish-state tests without actually uploading, plus manual upload verification only with a configured browser profile.

## Rollout

Implement in this order:

1. Phase 0: fix current breakage and docs.
2. Phase 1: add guardrails and validation.
3. Phase 2: improve subtitle quality.
4. Phase 4: improve content engine.
5. Phase 5: publish and schedule safety.
6. Phase 3: renderer track, because it has the biggest blast radius.

Renderer work can move earlier only after Phase 0 and Phase 1 are complete and all baseline checks pass.

## Non-Goals

- Do not remove MoviePy in this roadmap.
- Do not commit local secrets from `config.json`, `.env`, `.mp/`, cookies, profiles, generated media, or cache files.
- Do not make auto publish the default.
- Do not rewrite the whole frontend.
- Do not move runtime data out of `.mp/`.
- Do not call provider APIs directly from feature code.

## Open Decisions

- Whether Phase 3 should use Remotion or an HTML-native renderer first. Recommendation: start HTML-native because current app already has React UI but the render composition can stay plain HTML and avoid bundler coupling.
- Whether WhisperX should be local-only or provider-backed. Recommendation: optional local path first, because GPU and dependency size vary by machine.
- Whether scheduler UI belongs in main dashboard or a separate workspace. Recommendation: separate workspace after backend publish states are reliable.

## Spec Self-Review

- Completeness scan: no empty markers or deferred requirements remain.
- Consistency check: phases preserve existing modules and add new boundaries only where needed.
- Scope check: this is a master roadmap with independently implementable phases. Phase 0 and Phase 1 are the immediate implementation target.
- Ambiguity check: defaults, validation behavior, and non-goals are explicit.
