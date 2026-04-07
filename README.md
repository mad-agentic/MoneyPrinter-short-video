# MoneyPrinter Short Video

> 🇬🇧 English | [🇻🇳 Tiếng Việt](#tiếng-việt)

Automated short-video creation and distribution platform. Generates YouTube Shorts (and other platforms) using LLMs for scripting, Gemini for images, KittenTTS / OmniVoice for voiceover, Whisper / AssemblyAI for subtitles, MoviePy for video composition, and Selenium for publishing — all from a modern Web UI, running fully local.

> Requires **Python 3.12** and **Node.js 18+**

---

## Features

| Feature | Description |
|---|---|
| **YouTube Shorts** | Auto-generate script → images (Gemini AI) → voiceover (TTS) → subtitles → compose video → upload to YouTube |
| **Twitter/X Bot** | LLM-generated content, auto-post via Selenium |
| **Affiliate Marketing** | Scrape Amazon products, generate pitch with LLM, post to Twitter |
| **Outreach AI** | Scrape local businesses (Google Maps), find emails, send outreach automatically |
| **Research & Ideas** | Auto-search trends from Reddit / YouTube / TikTok, LLM analysis, generate 5 video ideas with full scripts — then create a YouTube session pre-filled and ready to generate |
| **Web UI** | React dashboard — manage all workflows, gallery, real-time logs |
| **CRON Jobs** | Schedule auto-posting (1–3 times/day) |
| **Multi-account** | Manage multiple YouTube and Twitter accounts in parallel |

### Pipeline highlights

- **Session-based pipeline** — Each video is a UUID session. Progress is saved at every stage; interrupted sessions can be resumed.
- **Stage direction cleanup** — LLM-generated stage markers (`Hook: (description)`, `→ Content: (...)`, B-roll annotations) are automatically stripped from audio text before TTS, so nothing unintended gets spoken or transcribed.
- **Auto-save script** — After AUTO BUILD, the generated script is automatically persisted to the session JSON without needing a manual Save click.
- **Media Engine follows session** — Selecting a session in the sidebar automatically filters the Media Engine gallery to that session's media. You can then change the gallery filter manually without it being overwritten.
- **Title audio toggle** — Optional title card audio (subject read aloud before main content) can be disabled in Settings.
- **Whisper progress logging** — Shows language detection, detected language + confidence, audio duration, and elapsed time during transcription so the process is no longer a black box.

---

## System Requirements

| Software | Version | Notes |
|---|---|---|
| Python | 3.12 | Required |
| Node.js | 18+ | Frontend |
| Firefox | Latest | Selenium automation |
| ImageMagick | 7.x | Subtitle overlay rendering |
| Ollama | Latest | Local LLM (or use any OpenAI-compatible API) |
| Go | 1.21+ | Only needed for Outreach feature |

---

## Installation

### Windows (Recommended)

**Step 1:** Clone or copy the project to your machine

**Step 2:** Configure `config.json`

```bash
copy config.example.json config.json
```

Open `config.json` and fill in the required values (see [Configuration](#configuration) below).

**Step 3:** Run the automated setup

```
setup.bat
```

This will automatically:
- Create a Python virtual environment (`venv/`)
- Install all Python dependencies (`requirements.txt`)
- Install npm packages for the frontend

### Manual (Windows / macOS / Linux)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install frontend packages
cd frontend && npm install && cd ..
```

---

## Running

### Windows

```
start_hub.bat
```

Opens two terminal windows:
- **Backend API** at `http://localhost:15001`
- **Frontend UI** at `http://localhost:5174`

Open your browser at: **http://localhost:5174**

### Manual

```bash
# Terminal 1 — Backend
cd src
..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload

# Terminal 2 — Frontend
cd frontend
npm run dev -- --port 5174
```

### CLI (no Web UI)

```bash
python src/main.py
```

### Headless / CRON

```bash
python src/cron.py twitter <account_uuid> <model>
python src/cron.py youtube <account_uuid> <model>
```

---

## Configuration

All configuration lives in `config.json`. Key settings:

### LLM Backend

```json
"llm_backend": "ollama",
"ollama_base_url": "http://127.0.0.1:11434",
"ollama_model": "llama3:latest"
```

Or use any OpenAI-compatible API (LM Studio, OpenRouter, etc.):

```json
"llm_backend": "openai_compatible",
"openai_base_url": "http://localhost:1234/v1",
"openai_model": "your-model-name",
"openai_api_key": "none"
```

### Image Generation (Gemini)

```json
"nanobanana2_api_key": "YOUR_GEMINI_API_KEY",
"nanobanana2_model": "gemini-3.1-flash-image-preview",
"nanobanana2_aspect_ratio": "9:16"
```

### Text-to-Speech

```json
"tts_engine": "kitten",
"tts_fallback_engine": "kitten",
"tts_voice": "Jasper"
```

Available voices: `Jasper`, `Luna`, `Milo`, `Ava`, `Emma`

To use OmniVoice as the primary engine:

```json
"tts_engine": "omnivoice",
"tts_fallback_engine": "kitten",
"omnivoice_model": "default",
"omnivoice_device": "cpu",
"omnivoice_dtype": "float32"
```

> If OmniVoice is not installed, run `pip install omnivoice` inside the virtual environment. The system will automatically fall back to the fallback engine if the primary is unavailable.

### Speech-to-Text (Subtitles)

```json
"stt_provider": "local_whisper",
"whisper_model": "base",
"whisper_device": "auto",
"whisper_compute_type": "int8",
"whisper_vad_filter": false,
"whisper_beam_size": 1
```

> On CPU, `tiny` model is ~3× faster than `base` and sufficient for translation tasks.

Using AssemblyAI instead:

```json
"stt_provider": "assembly_ai",
"assembly_ai_api_key": "YOUR_KEY"
```

### Firefox Profile

```json
"firefox_profile": "your-firefox-profile-name",
"headless": false
```

The Firefox profile must already be logged into YouTube and Twitter/X.

### Video & ImageMagick

```json
"imagemagick_path": "C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe",
"font": "bold_font.ttf",
"video_encode_preset": "veryfast",
"video_encode_crf": 24,
"threads": 2,
"enable_title_audio": true
```

`enable_title_audio` — set to `false` to skip reading the subject aloud as a title card at the beginning of the video.

### Email Outreach

```json
"email": {
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "username": "your@gmail.com",
  "password": "app-password"
}
```

---

## Project Structure

```
MoneyPrinter-short-video/
├── src/                        # Python backend
│   ├── api/                    # FastAPI routes
│   │   ├── main.py             # App entry, /system/* endpoints
│   │   ├── youtube.py          # /youtube/* routes
│   │   ├── twitter.py          # /twitter/* routes
│   │   ├── affiliate.py        # /affiliate/* routes
│   │   ├── research.py         # /research/* SSE streaming
│   │   ├── session_manager.py  # Session CRUD
│   │   └── log_stream.py       # SSE log streaming
│   ├── classes/                # Core pipeline classes
│   │   ├── YouTube.py          # Full video generation pipeline
│   │   ├── Twitter.py          # Tweet automation
│   │   ├── AFM.py              # Amazon affiliate
│   │   ├── Outreach.py         # Business outreach
│   │   └── Tts.py              # TTS wrapper (KittenTTS / OmniVoice)
│   ├── config.py               # Config reader
│   ├── cache.py                # JSON persistence (.mp/)
│   ├── llm_provider.py         # Ollama / OpenAI client + streaming
│   ├── research_engine.py      # Web search + LLM synthesis
│   ├── main.py                 # CLI interactive menu
│   └── cron.py                 # Headless scheduled runner
├── frontend/                   # React 19 + Vite + TypeScript
│   └── src/
│       ├── App.tsx             # Main UI (~3,500 lines)
│       └── ResearchWorkspace.tsx
├── fonts/                      # Subtitle font files
├── Songs/                      # Background music
├── scripts/                    # Utility scripts
│   ├── preflight_local.py      # Dependency checker
│   └── setup_local.sh          # macOS/Linux setup
├── .mp/                        # Runtime data (auto-created)
│   ├── sessions/               # Per-video session data
│   └── research/               # Research sessions
├── config.json                 # Your configuration
├── config.example.json         # Configuration template
├── requirements.txt
├── setup.bat                   # Windows first-run setup
└── start_hub.bat               # Windows launcher
```

---

## API Endpoints

Backend runs at `http://localhost:15001`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/system/status` | System health |
| GET | `/system/config` | Read config |
| PATCH | `/system/config` | Update config |
| GET | `/system/tts-health` | TTS engine status + warm-up state |
| GET | `/system/gallery` | List media files |
| GET | `/system/sessions` | List sessions |
| POST | `/system/sessions` | Create session |
| DELETE | `/system/sessions/{id}` | Delete session |
| GET | `/system/logs/stream` | SSE real-time log stream |
| GET | `/system/llm/models` | List available LLM models |
| POST | `/youtube/generate` | Start video generation |
| PATCH | `/youtube/sessions/{id}/meta` | Update session subject / script / metadata |
| POST | `/youtube/{account}/generate-audio-text` | Generate script with LLM |
| POST | `/youtube/{account}/translate-script` | Translate script to target language |
| POST | `/twitter/post` | Post tweet |
| POST | `/research/sessions` | Create research session |
| GET | `/research/sessions` | List research sessions |
| POST | `/research/sessions/{id}/chat` | Chat / research / generate ideas (SSE) |
| GET | `/research/sessions/{id}/ideas` | List generated ideas |

---

## YouTube Short — Generation Pipeline

```
1. Script Setup       → Enter subject; LLM generates script
2. Generate Images    → Gemini AI creates 9:16 illustrations
3. Generate Audio     → TTS converts cleaned script to WAV
4. Generate Subtitles → Whisper / AssemblyAI produces SRT
5. Compose Video      → MoviePy merges images + audio + subtitles + music
6. Ready for Review   → Preview in Web UI, edit metadata
7. Published          → Selenium uploads to YouTube
```

Each stage is resumable. If generation is interrupted at any step, select the session and re-run from where it left off using Custom Step mode.

---

## Research & Ideas

The **Research & Ideas** tab automates trend research and idea generation.

### How to use

1. Open the **Research & Ideas** tab in the sidebar
2. Click **Sessions** → enter a topic → **+ New**
3. Choose a mode and send a message:

| Mode | Function |
|---|---|
| 💬 **Chat** | Free-form Q&A with AI about content strategy |
| 🔍 **Research** | Auto web search (ddgs) → LLM analyzes trends |
| 💡 **Ideas** | Generate 5 complete video ideas (hook, script outline, CTA, format) |

4. Click **Create Video** on any idea card → automatically creates a new YouTube session pre-filled with subject and script

### How research works

```
Input topic
    ↓
Parallel search across 4 sources (ddgs — no API key needed):
  Web  ·  YouTube Shorts  ·  Reddit  ·  TikTok
    ↓
LLM synthesizes insights: trends, hooks, viral formats
    ↓
Ideas mode → LLM outputs 5 structured ideas (JSON)
    ↓
"Create Video" → YouTube workspace auto-filled
```

---

## Troubleshooting

**`venv` not found** — Run `setup.bat` first.

**Port already in use** — `start_hub.bat` automatically kills existing processes on ports 15001 and 5174.

**Firefox won't open** — Check `firefox_profile` in `config.json`; the profile must exist and already be logged in.

**ImageMagick error** — Ensure `imagemagick_path` points to the correct `magick.exe`.

**Ollama not connecting** — Run `ollama serve` and verify `ollama_base_url`.

**Frontend won't load** — Wait a few seconds after launching `start_hub.bat`; the backend needs time to start.

**Whisper stuck / no progress** — On CPU with `base` model, language detection alone can take 30–120 seconds before the first log appears. Progress is now logged every 10 seconds. Consider switching to `tiny` model for faster processing, or use AssemblyAI for cloud-based transcription.

**First audio generation is slow** — If using OmniVoice, the backend warms up the model at startup. Check status at `GET /system/tts-health` or the `TTS Engine` indicator in the Web UI sidebar.

**TTS shows degraded / warning** — Check `tts_engine`, `tts_fallback_engine`, and `omnivoice_*` keys in `config.json`. The system auto-falls back to the fallback engine if the primary is unavailable.

**Research returns "Connection error"** — LLM backend not responding. Check Ollama / LM Studio is running. The backend sends SSE heartbeats every 2 seconds; if LLM takes >2 minutes the connection will time out.

**Research search returns 0 results** — DuckDuckGo has rate limits. Wait 30–60 seconds and retry. The project uses the `ddgs` package (renamed from `duckduckgo_search`).

**Ideas not parsing as JSON** — LLM returned malformed JSON. Try a larger model, or run a Research query first to give the LLM context before switching to Ideas mode.

---

## License

Licensed under the `GNU Affero General Public License v3.0`. See [LICENSE](LICENSE) for details.

## Disclaimer

This project is intended for educational and research purposes only. The authors take no responsibility for any misuse.

---
---

# Tiếng Việt

> [🇬🇧 English](#moneyprinter-short-video) | 🇻🇳 Tiếng Việt

Nền tảng tự động hóa tạo và phân phối video ngắn. Tạo YouTube Shorts (và các nền tảng khác) sử dụng LLM cho kịch bản, Gemini cho hình ảnh, KittenTTS / OmniVoice cho lồng tiếng, Whisper / AssemblyAI cho phụ đề, MoviePy cho dựng video, và Selenium cho đăng bài — tất cả từ Web UI hiện đại, chạy hoàn toàn local.

> Yêu cầu **Python 3.12** và **Node.js 18+**

---

## Tính năng

| Tính năng | Mô tả |
|---|---|
| **YouTube Shorts** | Tự động tạo script → hình ảnh (Gemini AI) → lồng tiếng (TTS) → phụ đề → ghép video → upload lên YouTube |
| **Twitter/X Bot** | Tạo nội dung bằng LLM, đăng bài tự động qua Selenium |
| **Affiliate Marketing** | Scrape sản phẩm Amazon, tạo pitch bằng LLM, đăng lên Twitter |
| **Outreach AI** | Scrape doanh nghiệp (Google Maps), tìm email, gửi email outreach tự động |
| **Research & Ideas** | Tự động tìm xu hướng từ Reddit / YouTube / TikTok, phân tích bằng LLM, tạo 5 ý tưởng video có script — rồi tạo session YouTube mới, điền sẵn nội dung |
| **Web UI** | Dashboard React — quản lý toàn bộ workflow, gallery, log real-time |
| **CRON Jobs** | Lên lịch đăng bài tự động (1–3 lần/ngày) |
| **Multi-account** | Quản lý nhiều tài khoản YouTube và Twitter song song |

### Cải tiến mới

- **Dọn dẹp stage direction** — Các nhãn mô tả từ LLM (`Hook: (mô tả)`, `→ Content: (...)`, annotation B-roll) tự động bị xóa khỏi audio text trước khi đưa vào TTS, tránh TTS đọc nhầm.
- **Auto-save script** — Sau khi AUTO BUILD, script được tự động lưu vào session JSON, không cần nhấn Save thủ công.
- **Media Engine theo session** — Chọn session ở sidebar tự động lọc gallery Media Engine theo session đó. Sau đó thay đổi thủ công sẽ không bị ghi đè.
- **Tắt title audio** — Có thể tắt phần đọc tên chủ đề ở đầu video trong Settings.
- **Log tiến trình Whisper** — Hiển thị language detection, ngôn ngữ phát hiện + độ tin cậy, thời lượng audio, thời gian đã chạy trong quá trình transcription.

---

## Yêu cầu hệ thống

| Phần mềm | Phiên bản | Ghi chú |
|---|---|---|
| Python | 3.12 | Bắt buộc |
| Node.js | 18+ | Cho frontend |
| Firefox | Mới nhất | Selenium automation |
| ImageMagick | 7.x | Tạo subtitle overlay |
| Ollama | Mới nhất | LLM local (hoặc dùng OpenAI-compatible API) |
| Go | 1.21+ | Chỉ cần nếu dùng tính năng Outreach |

---

## Cài đặt

### Windows (Khuyến nghị)

**Bước 1:** Clone hoặc copy project về máy

**Bước 2:** Cấu hình `config.json`

```bash
copy config.example.json config.json
```

Mở `config.json` và điền các giá trị cần thiết (xem phần [Cấu hình](#cấu-hình) bên dưới).

**Bước 3:** Chạy setup tự động

```
setup.bat
```

Script sẽ tự động:
- Tạo Python virtual environment (`venv/`)
- Cài đặt tất cả Python dependencies
- Cài đặt npm packages cho frontend

### Thủ công (Windows / macOS / Linux)

```bash
python -m venv venv
.\venv\Scripts\activate          # Windows
source venv/bin/activate          # macOS/Linux
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

---

## Khởi chạy

### Windows

```
start_hub.bat
```

Mở 2 cửa sổ terminal:
- **Backend API** tại `http://localhost:15001`
- **Frontend UI** tại `http://localhost:5174`

Truy cập trình duyệt: **http://localhost:5174**

### Thủ công

```bash
# Terminal 1 — Backend
cd src && ..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload

# Terminal 2 — Frontend
cd frontend && npm run dev -- --port 5174
```

---

## Cấu hình

### LLM Backend

```json
"llm_backend": "ollama",
"ollama_base_url": "http://127.0.0.1:11434",
"ollama_model": "llama3:latest"
```

Hoặc OpenAI-compatible (LM Studio, OpenRouter...):

```json
"llm_backend": "openai_compatible",
"openai_base_url": "http://localhost:1234/v1",
"openai_model": "your-model-name",
"openai_api_key": "none"
```

### Image Generation (Gemini)

```json
"nanobanana2_api_key": "YOUR_GEMINI_API_KEY",
"nanobanana2_model": "gemini-3.1-flash-image-preview",
"nanobanana2_aspect_ratio": "9:16"
```

### Text-to-Speech

```json
"tts_engine": "kitten",
"tts_fallback_engine": "kitten",
"tts_voice": "Jasper"
```

Các giọng hỗ trợ: `Jasper`, `Luna`, `Milo`, `Ava`, `Emma`

Dùng OmniVoice:

```json
"tts_engine": "omnivoice",
"tts_fallback_engine": "kitten",
"omnivoice_model": "default",
"omnivoice_device": "cpu"
```

### Speech-to-Text (Phụ đề)

```json
"stt_provider": "local_whisper",
"whisper_model": "base",
"whisper_device": "auto",
"whisper_compute_type": "int8",
"whisper_beam_size": 1
```

> Trên CPU, model `tiny` nhanh hơn ~3× so với `base`, đủ dùng cho tác vụ dịch.

### Video & ImageMagick

```json
"imagemagick_path": "C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe",
"font": "bold_font.ttf",
"video_encode_preset": "veryfast",
"video_encode_crf": 24,
"enable_title_audio": true
```

`enable_title_audio: false` — bỏ qua phần đọc tên chủ đề ở đầu video.

---

## Quy trình tạo YouTube Short

```
1. Script Setup       → Nhập chủ đề; LLM tạo kịch bản
2. Generate Images    → Gemini AI tạo hình 9:16
3. Generate Audio     → TTS chuyển script thành WAV
4. Generate Subtitles → Whisper / AssemblyAI tạo SRT
5. Compose Video      → MoviePy ghép hình + audio + phụ đề + nhạc
6. Ready for Review   → Xem preview, chỉnh metadata
7. Published          → Selenium upload lên YouTube
```

Mỗi giai đoạn có thể resume. Nếu bị gián đoạn, chọn lại session và chạy tiếp từ bước cần thiết bằng Custom Step mode.

---

## Research & Ideas

### Cách dùng

1. Mở tab **Research & Ideas** trên sidebar
2. **Sessions** → nhập topic → **+ Mới**
3. Chọn mode:

| Mode | Chức năng |
|---|---|
| 💬 **Chat** | Hỏi đáp tự do với AI về content strategy |
| 🔍 **Research** | Tự động tìm kiếm web → LLM phân tích xu hướng |
| 💡 **Ideas** | Tạo 5 ý tưởng video đầy đủ (hook, outline, CTA) |

4. Click **Tạo Video** trên card → tự động tạo YouTube session mới, điền sẵn nội dung

---

## Troubleshooting

**Không tìm thấy venv** — Chạy `setup.bat` trước.

**Port đã được dùng** — `start_hub.bat` tự kill process cũ trên port 15001 và 5174.

**Firefox không mở** — Kiểm tra `firefox_profile` trong `config.json`.

**ImageMagick lỗi** — Đảm bảo `imagemagick_path` trỏ đúng `magick.exe`.

**Ollama không kết nối** — Chạy `ollama serve`, kiểm tra `ollama_base_url`.

**Whisper bị đứng / không có log** — Trên CPU, language detection có thể mất 30–120 giây trước khi xuất hiện log đầu tiên. Log tiến trình sẽ hiện mỗi 10 giây. Chuyển sang model `tiny` để tăng tốc, hoặc dùng AssemblyAI.

**Generate audio chậm lần đầu** — OmniVoice warm-up model khi khởi động. Kiểm tra tại `GET /system/tts-health` hoặc indicator `TTS Engine` trên sidebar.

**Research trả về lỗi kết nối** — Kiểm tra LLM backend (Ollama / LM Studio) đang chạy.

**Search trả về 0 kết quả** — DuckDuckGo rate limit. Đợi 30–60 giây rồi thử lại.

---

## License

Licensed under `GNU Affero General Public License v3.0`. Xem [LICENSE](LICENSE).

## Disclaimer

Project này chỉ dành cho mục đích học tập và nghiên cứu. Tác giả không chịu trách nhiệm về bất kỳ hành vi lạm dụng nào.
