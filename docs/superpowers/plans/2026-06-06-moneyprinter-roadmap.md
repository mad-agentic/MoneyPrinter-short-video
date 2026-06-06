# MoneyPrinter Roadmap Stabilization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize the current MoneyPrinter workflow, add provider/config guardrails, and create testable tracks for subtitle quality, deterministic rendering, content improvements, and publish safety.

**Architecture:** Phase 0 and Phase 1 make focused changes to the existing config, provider, Settings UI, preflight, and docs. Later phases add narrow boundaries for subtitles, rendering, content templates, duplicate detection, and scheduler/publish state without replacing the current YouTube workflow.

**Tech Stack:** Python 3.12, FastAPI, requests, MoviePy, faster-whisper, React 19, Vite, TypeScript, ESLint, 9Router-compatible HTTP APIs, FFmpeg.

---

## Scope Check

This roadmap covers multiple subsystems. Treat this plan as a master plan split into implementation tracks. Execute Phase 0 and Phase 1 first. After they pass verification, create smaller follow-up plans for Phase 2, Phase 3, Phase 4, and Phase 5 if the implementation needs more detail.

## File Structure

### Phase 0 And Phase 1 Files

- Modify `frontend/src/App.tsx`: typed Settings config model, `tavily/search` default, no `search-combo` auto-selection, model capability warnings.
- Modify `src/providers/ninerouter.py`: prefer `tavily/search`, normalize web model detection, mask keys in errors.
- Modify `src/config.py`: add public `get_config()` helper and use it in new validation helpers.
- Modify `scripts/preflight_local.py`: validate active provider mode and 9Router model capability fields without printing secrets.
- Modify `README.md`: align research model default and clarify publish requirements.
- Modify `readme_vn.md`: align Vietnamese docs with current defaults.
- Modify `docs/PROJECT_USAGE_VN.md`: add runtime warnings, provider capability guidance, and troubleshooting for STT/search model mismatch.

### Later Phase Files

- Modify `src/classes/YouTube.py`: subtitle formatting hooks, renderer selection, duplicate metadata, publish state persistence.
- Modify `src/research_engine.py`: source labels, duplicate-aware idea generation, glossary context.
- Modify `src/api/youtube.py`: renderer option, publish/scheduler state, duplicate checks.
- Modify `src/api/research.py`: glossary and source metadata if needed by Research UI.
- Modify `frontend/src/ResearchWorkspace.tsx`: source labels, format/template controls, handoff metadata.
- Create `src/renderers/__init__.py`: renderer package marker.
- Create `src/renderers/moviepy_renderer.py`: wrapper around existing MoviePy compose behavior once extraction is safe.
- Create `src/renderers/html_renderer.py`: HTML composition to MP4 prototype.
- Create `src/subtitles/formatting.py`: caption line-length and single-line formatting helpers.
- Create `src/subtitles/glossary.py`: glossary normalization and prompt formatting helpers.
- Create `src/scheduler.py` or extend `src/cron.py`: explicit publish schedule orchestration after Phase 5 design is approved.

## Phase 0: Stabilize Current App

### Task 1: Fix 9Router Search Defaults

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `src/providers/ninerouter.py`
- Modify: `README.md`
- Modify: `readme_vn.md`

- [x] **Step 1: Update frontend default search model**

In `frontend/src/App.tsx`, replace the Settings default:

```ts
search_model: 'search-combo',
```

with:

```ts
search_model: 'tavily/search',
```

- [x] **Step 2: Update frontend web model auto-selection**

In `fetchAvailableWebModels`, replace:

```ts
updateNineRouter({ search_model: models.includes('search-combo') ? 'search-combo' : models[0] });
```

with:

```ts
const preferredSearchModel = models.includes('tavily/search') ? 'tavily/search' : models[0];
updateNineRouter({ search_model: preferredSearchModel });
```

- [x] **Step 3: Update save fallback**

In `saveConfig`, replace:

```ts
search_model: String(currentNineRouter.search_model || 'search-combo'),
```

with:

```ts
search_model: String(currentNineRouter.search_model || 'tavily/search'),
```

- [x] **Step 4: Update provider preference order**

In `src/providers/ninerouter.py`, change `_select_web_model()` preferred tuple from:

```python
preferred = (
    "search-combo",
    "tavily/search",
    "tavily",
    "brave-search/search",
    "brave-search",
    "serper/search",
    "serper",
    "exa/search",
    "exa",
    "perplexity/search",
    "perplexity",
)
```

to:

```python
preferred = (
    "tavily/search",
    "tavily",
    "brave-search/search",
    "brave-search",
    "serper/search",
    "serper",
    "exa/search",
    "exa",
    "perplexity/search",
    "perplexity",
    "search-combo",
)
```

- [x] **Step 5: Update README defaults**

In `README.md`, replace `9Router \`search-combo\`` with `9Router \`tavily/search\``.

In `readme_vn.md`, replace `9Router \`search-combo\`` with `9Router \`tavily/search\``.

- [x] **Step 6: Verify search-combo no longer appears in source defaults**

Run:

```powershell
rg -n "search-combo" frontend\src\App.tsx src\providers\ninerouter.py README.md readme_vn.md docs\PROJECT_USAGE_VN.md config.example.json src\config.py
```

Expected: only one allowed occurrence in `src/providers/ninerouter.py` inside the final fallback list, or no occurrences if the team removes it entirely.

- [x] **Step 7: Commit Phase 0 search fix**

```powershell
git add frontend\src\App.tsx src\providers\ninerouter.py README.md readme_vn.md
git commit -m "fix: stabilize ninerouter search defaults"
```

### Task 2: Fix Settings TypeScript `any` Errors

**Files:**
- Modify: `frontend/src/App.tsx`

- [x] **Step 1: Add config interfaces near existing frontend interfaces**

Add these TypeScript interfaces after `interface ResearchIdeaPrefill`:

```ts
interface NineRouterConfig {
  enabled: boolean;
  base_url: string;
  api_key: string;
  chat_model: string;
  image_model: string;
  image_size: string;
  tts_model: string;
  tts_voice: string;
  tts_response_format: string;
  stt_model: string;
  stt_response_format: string;
  search_model: string;
  search_max_results: number;
}

interface ProvidersConfig {
  ninerouter: NineRouterConfig;
  local: { enabled: boolean };
  [key: string]: unknown;
}

interface AiProviderConfig {
  active: string;
  fallback_to_local: boolean;
}

interface AppConfig {
  verbose: boolean;
  headless: boolean;
  threads: number;
  is_for_kids: boolean;
  stt_provider: string;
  whisper_model: string;
  whisper_device: string;
  whisper_compute_type: string;
  whisper_vad_filter: boolean;
  whisper_beam_size: number;
  tts_engine: string;
  tts_fallback_engine: string;
  tts_voice: string;
  tts_strict_mode: boolean;
  enable_title_audio: boolean;
  video_encode_preset: string;
  video_encode_crf: number;
  script_sentence_length: number;
  font: string;
  llm_backend: string;
  ollama_base_url: string;
  ollama_model: string;
  openai_base_url: string;
  openai_model: string;
  openai_api_key: string;
  ai_provider: AiProviderConfig;
  providers: ProvidersConfig;
}
```

- [x] **Step 2: Type the config state**

Change:

```ts
const [cfg, setCfg] = useState({
```

to:

```ts
const [cfg, setCfg] = useState<AppConfig>({
```

- [x] **Step 3: Replace `any` provider reads**

Replace:

```ts
const currentProviders = (cfg as any).providers || {};
const currentNineRouter = currentProviders.ninerouter || {};
```

with:

```ts
const currentProviders = cfg.providers;
const currentNineRouter = currentProviders.ninerouter;
```

- [x] **Step 4: Replace `any` TTS reads**

Replace each `(cfg as any).tts_engine` with `cfg.tts_engine`.

Replace each `(cfg as any).tts_fallback_engine` with `cfg.tts_fallback_engine`.

Replace state updates shaped like:

```ts
setCfg(prev => ({ ...prev, tts_engine: e.target.value } as any))
```

with:

```ts
setCfg(prev => ({ ...prev, tts_engine: e.target.value }))
```

- [x] **Step 5: Type nested update helpers**

Replace:

```ts
const nrCfg = ((cfg as any).providers?.ninerouter || {}) as Record<string, any>;
const updateNineRouter = (patch: Record<string, any>) => {
  setCfg(prev => ({
    ...prev,
    providers: {
      ...((prev as any).providers || {}),
      ninerouter: {
        ...(((prev as any).providers || {}).ninerouter || {}),
        ...patch,
      },
      local: { enabled: true },
    },
  } as any));
};
const updateAiProvider = (patch: Record<string, any>) => {
  setCfg(prev => ({
    ...prev,
    ai_provider: {
      ...((prev as any).ai_provider || {}),
      ...patch,
    },
  } as any));
};
```

with:

```ts
const nrCfg = cfg.providers.ninerouter;
const updateNineRouter = (patch: Partial<NineRouterConfig>) => {
  setCfg(prev => ({
    ...prev,
    providers: {
      ...prev.providers,
      ninerouter: {
        ...prev.providers.ninerouter,
        ...patch,
      },
      local: { enabled: true },
    },
  }));
};
const updateAiProvider = (patch: Partial<AiProviderConfig>) => {
  setCfg(prev => ({
    ...prev,
    ai_provider: {
      ...prev.ai_provider,
      ...patch,
    },
  }));
};
```

- [x] **Step 6: Run frontend lint**

```powershell
cd frontend
npm run lint
```

Expected: no `@typescript-eslint/no-explicit-any` errors in `frontend/src/App.tsx`. Existing hook warnings in `ResearchWorkspace.tsx` can remain for a separate task if they are warnings only.

- [x] **Step 7: Run frontend build**

```powershell
cd frontend
npm run build
```

Expected: TypeScript build and Vite build pass.

- [x] **Step 8: Commit Settings typing**

```powershell
git add frontend\src\App.tsx
git commit -m "fix: type settings config state"
```

### Task 3: Normalize Local Config For Current Runtime

**Files:**
- Modify: `config.json` only if this is the user's local workspace and the user asked to fix runtime config.
- Modify: `docs/PROJECT_USAGE_VN.md`

- [x] **Step 1: Update local STT/TTS provider values if fixing current machine**

Because `config.json` contains secrets and is ignored, do not commit it. Set these local values only when the user wants the current machine fixed:

```json
"stt_provider": "local_whisper",
"providers": {
  "ninerouter": {
    "tts_model": "edge-tts/vi-VN-HoaiMyNeural",
    "tts_voice": "vi-VN-HoaiMyNeural",
    "stt_model": "gemini/gemini-2.5-flash",
    "search_model": "tavily/search"
  }
}
```

Rationale: local Whisper already succeeds in the observed logs. Use 9Router STT only after `/v1/models/stt` confirms the configured model supports STT.

- [x] **Step 2: Document capability mismatch errors**

Add this troubleshooting section to `docs/PROJECT_USAGE_VN.md`:

````markdown
### Lỗi 9Router model sai capability

Ví dụ:

```text
Provider 'codex' does not support STT
Unknown provider: search-combo
```

Ý nghĩa: model/provider đang chọn không hỗ trợ đúng chức năng. Chat model không dùng cho STT/TTS/search được nếu 9Router không map capability đó.

Cách xử lý:

1. Với search, dùng `providers.ninerouter.search_model = "tavily/search"` hoặc model có trong `/v1/models/web`.
2. Với STT, dùng model có trong `/v1/models/stt`; nếu chưa chắc, đặt `stt_provider = "local_whisper"`.
3. Với TTS, dùng model có trong `/v1/models/tts`; tiếng Việt nên dùng `edge-tts/vi-VN-HoaiMyNeural` nếu server hỗ trợ.
4. Không điền chat model như `cx/gpt-5.5` vào `stt_model` hoặc `tts_model` trừ khi `/v1/models/stt` hoặc `/v1/models/tts` liệt kê đúng model đó.
````

- [x] **Step 3: Verify local config JSON remains valid**

```powershell
python -m json.tool config.json
```

Expected: valid JSON. Do not print API keys in final notes.

## Phase 1: Provider And Config Guardrails

### Task 4: Add Public `get_config()` Helper

**Files:**
- Modify: `src/config.py`

- [x] **Step 1: Add helper near `_read_config_json()`**

In `src/config.py`, replace:

```python
def _read_config_json() -> dict:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)
```

with:

```python
def get_config() -> dict:
    """Return the parsed local config.json with UTF-8 BOM tolerance."""
    with open(os.path.join(ROOT_DIR, "config.json"), "r", encoding="utf-8-sig") as file:
        return json.load(file)

def _read_config_json() -> dict:
    return get_config()
```

- [x] **Step 2: Verify imports compile**

```powershell
python -m py_compile src\config.py src\llm_provider.py src\providers\registry.py
```

Expected: no output and exit code 0.

- [x] **Step 3: Commit config helper**

```powershell
git add src\config.py
git commit -m "chore: expose shared config helper"
```

### Task 5: Add 9Router Capability Validation To Preflight

**Files:**
- Modify: `scripts/preflight_local.py`

- [x] **Step 1: Add secret masking helper**

Add near `check_url()`:

```python
def mask_secret(value: str) -> str:
    text = str(value or "")
    if len(text) <= 8:
        return "***" if text else ""
    return f"{text[:4]}...{text[-4:]}"
```

- [x] **Step 2: Add 9Router GET helper**

Add below `mask_secret()`:

```python
def fetch_ninerouter_models(base_url: str, api_key: str, path: str) -> tuple[bool, list[str], str]:
    url = f"{base_url.rstrip('/')}/v1/{path.lstrip('/')}"
    headers = {}
    if api_key and api_key.lower() != "none":
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if not response.ok:
            return False, [], f"HTTP {response.status_code}: {response.text[:200].replace(api_key, '***')}"
        body = response.json()
        data = body.get("data", body if isinstance(body, list) else [])
        models = []
        for item in data:
            if isinstance(item, str):
                models.append(item)
            elif isinstance(item, dict):
                model_id = item.get("id") or item.get("name") or item.get("model")
                if model_id:
                    models.append(str(model_id))
        return True, sorted(set(models)), "ok"
    except Exception as exc:
        return False, [], str(exc).replace(api_key, "***")
```

- [x] **Step 3: Validate active 9Router settings**

After the Nano Banana base URL check, add:

```python
    ai_provider = cfg.get("ai_provider", {}) if isinstance(cfg.get("ai_provider"), dict) else {}
    providers = cfg.get("providers", {}) if isinstance(cfg.get("providers"), dict) else {}
    nr = providers.get("ninerouter", {}) if isinstance(providers.get("ninerouter"), dict) else {}
    ninerouter_active = ai_provider.get("active") == "ninerouter" and bool(nr.get("enabled", False))

    if ninerouter_active:
        nr_base = str(nr.get("base_url", cfg.get("openai_base_url", "http://localhost:20128"))).rstrip("/")
        if nr_base.endswith("/v1"):
            nr_base = nr_base[:-3]
        nr_key = str(nr.get("api_key", cfg.get("openai_api_key", "none")) or "none")
        ok(f"9Router active at {nr_base} with key={mask_secret(nr_key)}")

        capability_checks = [
            ("models/tts", "tts_model", str(nr.get("tts_model", ""))),
            ("models/stt", "stt_model", str(nr.get("stt_model", ""))),
            ("models/web", "search_model", str(nr.get("search_model", ""))),
        ]
        for path, key, selected in capability_checks:
            reachable, models, detail = fetch_ninerouter_models(nr_base, nr_key, path)
            if not reachable:
                warn(f"Could not validate 9Router {key} via /v1/{path}: {detail}")
                continue
            if selected and selected in models:
                ok(f"9Router {key} is listed in /v1/{path}: {selected}")
            elif selected:
                warn(f"9Router {key} is not listed in /v1/{path}: {selected}")
            else:
                warn(f"9Router {key} is empty")
```

- [x] **Step 4: Run preflight**

```powershell
python scripts\preflight_local.py
```

Expected: script never prints full API keys. Existing local setup failures may remain, but 9Router capability messages appear when provider is active.

- [x] **Step 5: Commit preflight guardrails**

```powershell
git add scripts\preflight_local.py
git commit -m "feat: validate ninerouter preflight config"
```

### Task 6: Update Runtime Documentation

**Files:**
- Modify: `docs/PROJECT_USAGE_VN.md`
- Modify: `README.md`
- Modify: `readme_vn.md`

- [x] **Step 1: Document `start_hub.bat` port behavior**

Add to the run section in `docs/PROJECT_USAGE_VN.md`:

```markdown
Lưu ý: `start_hub.bat` sẽ kiểm tra port `15001` và `5174`. Nếu port đang bị process khác giữ, script sẽ kill PID đó trước khi mở backend/frontend mới. Nếu đang chạy service quan trọng trên hai port này, hãy tắt thủ công hoặc đổi port trước.
```

- [x] **Step 2: Clarify TikTok/Instagram publishing**

In `README.md` and `readme_vn.md`, change claims that imply TikTok/Instagram always work automatically to say they require PostBridge config.

English wording:

```markdown
- **TikTok + Instagram** — available through PostBridge when `post_bridge.enabled`, API key, platforms, and account IDs are configured.
```

Vietnamese wording:

```markdown
- **TikTok + Instagram** — dùng qua PostBridge khi đã cấu hình `post_bridge.enabled`, API key, platforms và account IDs.
```

- [x] **Step 3: Clarify manual review default**

Add to both README files:

```markdown
Manual review is the default publish mode. Auto publish should be enabled only after account paths, metadata, and output video are verified.
```

Vietnamese:

```markdown
Manual review là chế độ mặc định. Chỉ bật auto publish sau khi đã kiểm tra account path, metadata và video output.
```

- [x] **Step 4: Run doc search checks**

```powershell
rg -n "search-combo|PostBridge|manual review|Manual review|start_hub" README.md readme_vn.md docs\PROJECT_USAGE_VN.md
```

Expected: no `search-combo`; PostBridge and manual review language present.

- [x] **Step 5: Commit docs**

```powershell
git add README.md readme_vn.md docs\PROJECT_USAGE_VN.md
git commit -m "docs: align runtime workflow guidance"
```

## Phase 2: Subtitle And Dubbing Quality

### Task 7: Add Subtitle Formatting Helpers

**Files:**
- Create: `src/subtitles/__init__.py`
- Create: `src/subtitles/formatting.py`
- Modify later: `src/classes/YouTube.py`

- [x] **Step 1: Create subtitle package marker**

Create `src/subtitles/__init__.py` with:

```python
"""Subtitle formatting helpers for MoneyPrinter."""
```

- [x] **Step 2: Create line formatting helper**

Create `src/subtitles/formatting.py` with:

```python
import re

def normalize_caption_text(text: str) -> str:
    """Collapse whitespace and remove structural labels from spoken captions."""
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    value = re.sub(r"^(Hook|CTA|Main points?|Nội dung|Kịch bản):\s*", "", value, flags=re.IGNORECASE)
    return value.strip()

def split_single_line_caption(text: str, max_chars: int = 42) -> list[str]:
    """Split caption text into single-line chunks for vertical short video."""
    normalized = normalize_caption_text(text)
    if not normalized:
        return []
    words = normalized.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines
```

- [x] **Step 3: Add focused tests if a test framework exists**

If the repo has no pytest setup, run a direct Python smoke check:

```powershell
python -c "from src.subtitles.formatting import split_single_line_caption; assert split_single_line_caption('Hook: một hai ba', 8) == ['một hai', 'ba']"
```

Expected: exit code 0.

- [x] **Step 4: Integrate only after helper passes**

In `src/classes/YouTube.py`, use `normalize_caption_text()` before writing generated subtitle preview text. Keep existing SRT timing logic unchanged in the first subtitle phase.

- [x] **Step 5: Verify subtitle helpers compile**

```powershell
python -m py_compile src\subtitles\__init__.py src\subtitles\formatting.py src\classes\YouTube.py
```

Expected: no output and exit code 0.

## Phase 3: Deterministic Renderer Track

### Task 8: Add Renderer Interface Without Changing Default Compose

**Files:**
- Create: `src/renderers/__init__.py`
- Create: `src/renderers/base.py`
- Create in Phase 3 follow-up: `src/renderers/html_renderer.py`
- Modify later: `src/classes/YouTube.py`

- [x] **Step 1: Create renderer package marker**

Create `src/renderers/__init__.py` with:

```python
"""Video renderer implementations for MoneyPrinter."""
```

- [x] **Step 2: Create renderer protocol**

Create `src/renderers/base.py` with:

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass
class RenderRequest:
    session_id: str
    subject: str
    image_paths: list[str]
    audio_path: str
    subtitle_path: str
    output_path: str
    width: int = 1080
    height: int = 1920

class VideoRenderer(Protocol):
    def render(self, request: RenderRequest) -> str:
        """Render a video and return the output path."""
```

- [x] **Step 3: Compile renderer package**

```powershell
python -m py_compile src\renderers\__init__.py src\renderers\base.py
```

Expected: no output and exit code 0.

- [x] **Step 4: Keep MoviePy default**

Do not modify `YouTube.combine()` until the interface exists and Phase 0/1 checks pass. The first renderer PR should add the interface only.

## Phase 4: Content Engine Improvements

### Task 9: Add Duplicate Key Helper

**Files:**
- Create: `src/content_fingerprint.py`
- Modify later: `src/api/session_manager.py`
- Modify later: `src/api/youtube.py`

- [x] **Step 1: Create deterministic fingerprint helper**

Create `src/content_fingerprint.py` with:

```python
import hashlib
import re

def normalize_content_key(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip().lower())
    return text

def content_fingerprint(subject: str, script: str = "") -> str:
    payload = f"{normalize_content_key(subject)}\n{normalize_content_key(script)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
```

- [x] **Step 2: Smoke test helper**

```powershell
python -c "from src.content_fingerprint import content_fingerprint; assert content_fingerprint(' A  B ') == content_fingerprint('a b')"
```

Expected: exit code 0.

- [x] **Step 3: Integrate in session metadata later**

When generating or creating a draft session, save `content_fingerprint(subject, script)` in `session.json`. Before `force_new_session=False` generation, search sessions for the same fingerprint and warn/reuse.

## Phase 5: Publish And Schedule Safety

### Task 10: Add Publish State Vocabulary

**Files:**
- Modify: `src/api/youtube.py`
- Modify: `src/api/session_manager.py` only if helper constants are needed.
- Modify: `docs/PROJECT_USAGE_VN.md`

- [x] **Step 1: Define publish state names in docs first**

Add to `docs/PROJECT_USAGE_VN.md`:

```markdown
Publish state nên dùng thống nhất:

- `ready_for_review`: video đã render, chưa upload.
- `published`: upload thành công.
- `publish_failed`: upload lỗi, có thể retry.
- `publish_skipped`: user hoặc config bỏ qua upload.
- `crosspost_skipped`: PostBridge tắt hoặc chưa cấu hình.
- `crosspost_failed`: PostBridge lỗi sau khi YouTube upload.
```

- [x] **Step 2: Persist skipped cross-post state**

In `src/api/youtube.py`, after `maybe_crosspost_youtube_short(...)`, capture the return value:

```python
crosspost_result = maybe_crosspost_youtube_short(
    video_path=youtube.video_path,
    title=youtube.metadata.get("title", ""),
    interactive=False,
)
```

Then save it in session metadata:

```python
session.save_stage(
    "published",
    metadata=youtube.metadata,
    crosspost_status=(
        "posted" if crosspost_result is True else
        "failed" if crosspost_result is False else
        "skipped"
    ),
)
```

- [x] **Step 3: Verify YouTube API compiles**

```powershell
python -m py_compile src\api\youtube.py src\post_bridge_integration.py
```

Expected: no output and exit code 0.

## Final Verification For Phase 0 And Phase 1

- [x] **Run backend compile suite**

```powershell
python -m py_compile src\config.py src\llm_provider.py src\research_engine.py src\providers\__init__.py src\providers\registry.py src\providers\ninerouter.py src\api\main.py src\api\youtube.py src\classes\Tts.py src\classes\YouTube.py
```

Expected: no output and exit code 0.

- [x] **Run JSON validation**

```powershell
python -m json.tool config.example.json
python -m json.tool config.json
```

Expected: both commands output formatted JSON and exit code 0. Do not paste secret values into final reports.

- [x] **Run preflight**

```powershell
python scripts\preflight_local.py
```

Expected: pass when local dependencies are configured. If local machine intentionally lacks Ollama, Firefox profile, or ImageMagick, report those as environment issues rather than code failures.

- [x] **Run frontend checks**

```powershell
cd frontend
npm run lint
npm run build
```

Expected: lint and build pass. If only React hook warnings remain and lint exits 0, record warnings in final notes.

- [x] **Run search drift check**

```powershell
rg -n "search-combo|tavily/search|Provider 'codex' does not support STT|Unknown provider: search-combo" README.md readme_vn.md docs\PROJECT_USAGE_VN.md frontend\src\App.tsx src\providers\ninerouter.py src\config.py config.example.json
```

Expected: `tavily/search` present in defaults/docs. `search-combo` absent except optional legacy fallback in `src/providers/ninerouter.py` if intentionally retained.

## Plan Self-Review

- Spec coverage: Phase 0 fixes active 9Router/doc/lint drift. Phase 1 adds config and preflight guardrails. Phase 2 covers subtitle direction. Phase 3 covers renderer direction. Phase 4 covers source/duplicate/content improvements. Phase 5 covers publish safety.
- Completeness scan: no empty tasks or undefined file paths remain.
- Type consistency: frontend interfaces match fields already used in `ConfigWorkspace`.
- Execution order: Phase 0 and Phase 1 are first because later tracks depend on stable provider/config behavior.

## Completion Addendum

- [x] Phase 2 now includes `src/subtitles/glossary.py` and `src/subtitles/adaptation.py` for terminology parsing, prompt context, label cleanup, glossary application, and TTS-ready adapted script metadata.
- [x] Phase 3 now includes `src/renderers/html_renderer.py` and `src/renderers/registry.py`. MoviePy remains default; HTML renderer writes deterministic composition HTML in dry-run mode until browser + FFmpeg execution is wired.
- [x] Phase 4 now includes `src/content_engine.py` for short templates, source labels, style presets, and deterministic media selection. YouTube generation stores `content_plan` and `media_selection` in session metadata.
- [x] Phase 5 now includes `src/scheduler.py` plus `POST /youtube/sessions/{session_id}/schedule` for serializing publish jobs to `.mp/publish_queue.json` and marking sessions as `scheduled`.
- [x] Regression coverage added in `tests/test_phase_completion.py` for glossary/adaptation, HTML renderer, content plan/media picker, and scheduler queue helpers.
- [x] Frontend advanced controls added in `frontend/src/App.tsx` for `template`, `style_preset`, `renderer`, `glossary`, `schedule_at`, and `schedule_platforms`.
