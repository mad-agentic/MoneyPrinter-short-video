# Script CC For Vietnamese Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Script CC mode that uses normalized TTS text as caption text, fixing Vietnamese CC corruption while keeping Whisper CC available.

**Architecture:** Add a deterministic backend SRT builder: script text plus audio duration becomes valid SRT. Route YouTube subtitle generation by `cc_mode`: `script`, `whisper`, or `auto`. Expose mode in React UI and default Vietnamese to Script CC.

**Tech Stack:** Python/FastAPI, `moviepy.AudioFileClip`, existing `subtitles.formatting.normalize_caption_text`, React/Vite, pytest, `py_compile`, frontend build.

---

## Files

- Create: `src/subtitles/script_srt.py` - build SRT from trusted script text.
- Create: `tests/test_script_srt.py` - cover Vietnamese preservation, splitting, timing.
- Modify: `src/classes/YouTube.py` - add `cc_mode`, script subtitle method, routing.
- Modify: `src/api/youtube.py` - accept/pass/save `cc_mode`.
- Modify: `frontend/src/App.tsx` - add selector, labels, request field.
- Modify: `config.example.json` - document default `cc_mode`.

---

### Task 1: Script SRT Helper

**Files:**
- Create: `src/subtitles/script_srt.py`
- Create: `tests/test_script_srt.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_script_srt.py`:

```python
from src.subtitles.script_srt import build_script_srt, split_script_captions


def test_split_preserves_vietnamese_words_and_diacritics():
    chunks = split_script_captions(
        "Trong crypto, một cú click sai có thể mất toàn bộ tiền. Đừng nhập seed phrase vào link lạ.",
        max_chars=52,
    )
    assert chunks == [
        "Trong crypto, một cú click sai có thể mất toàn bộ tiền.",
        "Đừng nhập seed phrase vào link lạ.",
    ]


def test_split_long_sentence_by_words():
    text = "Một câu rất dài không có dấu chấm cần được chia thành nhiều dòng ngắn để subtitle dễ đọc trên video dọc"
    chunks = split_script_captions(text, max_chars=42)
    assert all(len(chunk) <= 42 for chunk in chunks)
    assert " ".join(chunks) == text


def test_build_script_srt_uses_full_audio_duration():
    srt = build_script_srt("Câu một ngắn. Câu hai dài hơn một chút.", duration_seconds=6.0, max_chars=52)
    assert "1\n00:00:00,000 -->" in srt
    assert "2\n" in srt
    assert "00:00:06,000" in srt
    assert "Câu một ngắn." in srt
    assert "Câu hai dài hơn một chút." in srt


def test_build_script_srt_returns_empty_for_blank_text():
    assert build_script_srt("   ", duration_seconds=10.0) == ""
```

- [ ] **Step 2: Run fail check**

Run:

```powershell
python -m pytest tests\test_script_srt.py -q
```

Expected: fail because `src.subtitles.script_srt` does not exist.

- [ ] **Step 3: Implement helper**

Create `src/subtitles/script_srt.py`:

```python
import re

from subtitles.formatting import normalize_caption_text


def format_srt_timestamp(seconds: float) -> str:
    total_millis = max(0, int(round(float(seconds or 0) * 1000)))
    hours = total_millis // 3_600_000
    minutes = (total_millis % 3_600_000) // 60_000
    secs = (total_millis % 60_000) // 1000
    millis = total_millis % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _split_long_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if current and len(candidate) > max_chars:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


def split_script_captions(text: str, max_chars: int = 84) -> list[str]:
    normalized = normalize_caption_text(text)
    if not normalized:
        return []
    chunks: list[str] = []
    for sentence in re.split(r"(?<=[.!?。！？])\s+", normalized):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) <= max_chars:
            chunks.append(sentence)
        else:
            chunks.extend(_split_long_text(sentence, max_chars=max_chars))
    return chunks


def build_script_srt(text: str, duration_seconds: float, max_chars: int = 84) -> str:
    chunks = split_script_captions(text, max_chars=max_chars)
    if not chunks:
        return ""
    duration = max(float(duration_seconds or 0), len(chunks) * 1.2)
    total_chars = max(1, sum(len(chunk) for chunk in chunks))
    cursor = 0.0
    lines: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        if index == len(chunks):
            end = duration
        else:
            share = duration * (len(chunk) / total_chars)
            end = min(duration, max(cursor + 0.8, cursor + share))
        lines.extend([
            str(index),
            f"{format_srt_timestamp(cursor)} --> {format_srt_timestamp(end)}",
            chunk,
            "",
        ])
        cursor = end
    return "\n".join(lines).strip() + "\n"
```

- [ ] **Step 4: Run pass check**

Run:

```powershell
python -m pytest tests\test_script_srt.py -q
```

Expected: `4 passed`.

---

### Task 2: Backend CC Mode Routing

**Files:**
- Modify: `src/classes/YouTube.py`

- [ ] **Step 1: Add mode state**

In `YouTube.__init__`, near `self.enable_cc`, add:

```python
self.cc_mode: str = "auto"  # auto | script | whisper
```

- [ ] **Step 2: Add script subtitle method**

Add near `generate_subtitles_ninerouter`:

```python
def generate_subtitles_from_script(self, audio_path: str) -> str:
    from subtitles.script_srt import build_script_srt

    srt_dir = self._session.audio_dir if self._session else os.path.join(ROOT_DIR, ".mp")
    srt_path = os.path.join(srt_dir, str(uuid4()) + ".srt")
    duration = self._get_audio_duration() or 0
    if audio_path and os.path.exists(audio_path):
        audio_clip = AudioFileClip(audio_path)
        try:
            duration = float(audio_clip.duration or duration or 0)
        finally:
            audio_clip.close()
    srt_content = build_script_srt(self.script, duration_seconds=duration)
    if not srt_content.strip():
        raise RuntimeError("Script CC requested but script text is empty")
    with open(srt_path, "w", encoding="utf-8") as file:
        file.write(srt_content)
    if not self._ensure_valid_srt(srt_path, audio_path):
        raise RuntimeError("Script CC did not produce valid SRT subtitles")
    info(f"    Script CC generated from normalized text: {srt_path}")
    return srt_path
```

- [ ] **Step 3: Route in `generate_subtitles`**

After provider logging in `generate_subtitles`, add:

```python
mode = str(getattr(self, "cc_mode", "auto") or "auto").strip().lower()
if mode not in {"auto", "script", "whisper"}:
    mode = "auto"
if mode == "auto":
    mode = "whisper" if translate_to_english else "script"
info(f"    CC mode: {mode}")
if mode == "script":
    if translate_to_english:
        warning("Script CC cannot translate subtitles. Using Whisper CC for English subtitle mode.")
    else:
        return self.generate_subtitles_from_script(audio_path)
```

Leave existing Whisper/AssemblyAI/9Router STT routing below this block.

- [ ] **Step 4: Compile**

Run:

```powershell
python -m py_compile src\classes\YouTube.py src\subtitles\script_srt.py
```

Expected: no output.

---

### Task 3: API CC Mode

**Files:**
- Modify: `src/api/youtube.py`

- [ ] **Step 1: Add request field**

Add to `GenerateRequest` and `SubtitlePreviewRequest`:

```python
cc_mode: str = "auto"  # auto | script | whisper
```

- [ ] **Step 2: Pass to generation**

Add `cc_mode: str = "auto"` to `generate_and_upload_video(...)`, set:

```python
youtube.cc_mode = str(cc_mode or "auto").strip().lower()
```

Pass `req.cc_mode` from the endpoint call into `generate_and_upload_video`.

- [ ] **Step 3: Pass to preview**

In `generate-cc-preview`, after `youtube.enable_cc`, add:

```python
youtube.cc_mode = str(req.cc_mode or "auto").strip().lower()
```

Add to `session.save_stage(...)` and response:

```python
cc_mode=youtube.cc_mode,
```

```python
"cc_mode": youtube.cc_mode,
```

- [ ] **Step 4: Compile**

Run:

```powershell
python -m py_compile src\api\youtube.py src\classes\YouTube.py
```

Expected: no output.

---

### Task 4: Frontend Selector

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Add state**

Near `ccPreview` state, add:

```tsx
const [ccMode, setCcMode] = useState<'script' | 'whisper'>('script');
```

- [ ] **Step 2: Vietnamese default**

Add effect near language/voice effects:

```tsx
useEffect(() => {
  if (scriptLanguage === 'vietnamese' && !englishCcBottom) {
    setCcMode('script');
  }
}, [scriptLanguage, englishCcBottom]);
```

- [ ] **Step 3: Send request field**

Add to CC preview and generate request bodies:

```tsx
cc_mode: ccMode,
```

- [ ] **Step 4: Add selector and labels**

In Step 3 subtitle header controls, before the generate button, add:

```tsx
<select
  value={ccMode}
  onChange={(e) => setCcMode(e.target.value as 'script' | 'whisper')}
  className="bg-slate-950/80 border border-amber-500/30 rounded-md px-2 py-1 text-[10px] text-amber-100 focus:outline-none"
>
  <option value="script">Script CC</option>
  <option value="whisper">Whisper CC</option>
</select>
```

Change button text:

```tsx
{generatingCcPreview ? 'Generating...' : ccMode === 'script' ? 'Gen Script CC' : 'Gen Whisper CC'}
```

Change label text to show `Script CC (từ text chuẩn)` or `Whisper CC (từ audio thật)`.

- [ ] **Step 5: Build**

Run:

```powershell
cd frontend
npm run build
```

Expected: build succeeds.

---

### Task 5: Config And Smoke Verification

**Files:**
- Modify: `config.example.json`

- [ ] **Step 1: Document default**

Add near subtitle/STT config:

```json
"cc_mode": "script",
```

Meanings:

```text
script = use normalized Audio Text as caption text
whisper = transcribe generated audio
auto = backend chooses script unless English translated captions are requested
```

- [ ] **Step 2: Smoke Script CC**

Run with existing audio from earlier TTS smoke:

```powershell
$env:PYTHONIOENCODING="utf-8"
cd C:\Users\admin\Desktop\_AI\MoneyPrinter-short-video\src
..\venv\Scripts\python.exe -c "from classes.YouTube import YouTube; yt=YouTube('crypto','vietnamese'); yt.script='Trong crypto, một cú click sai có thể mất toàn bộ tiền. Đừng nhập seed phrase vào link lạ.'; yt.cc_mode='script'; srt=yt.generate_subtitles_from_script('C:/tmp/ninerouter-tts-class-test-utf8.mp3'); print(open(srt, encoding='utf-8').read())"
```

Expected: SRT contains exact Vietnamese terms: `crypto`, `click`, `seed phrase`.

- [ ] **Step 3: Full verification**

Run:

```powershell
python -m pytest tests\test_script_srt.py -q
python -m py_compile src\api\youtube.py src\classes\YouTube.py src\subtitles\script_srt.py
cd frontend
npm run build
```

Expected: all pass.

---

## Rollout Notes

- Keep Whisper CC. It is still useful for uploaded audio or no trusted script.
- Vietnamese should default to Script CC because text is already authoritative.
- English translated bottom captions should keep Whisper until a separate translated-script SRT path exists.
- Do not remove `faster-whisper`; add safer path, no replacement.

## Self-Review

- Spec coverage: fixes Vietnamese CC corruption, preserves Whisper mode, covers UI/API/backend/tests/config.
- Placeholder scan: no TBD/TODO, exact files and commands included.
- Type consistency: `cc_mode` values are `auto`, `script`, `whisper`; frontend uses `script | whisper`; backend accepts all three.
