# MoneyPrinter Short Video

Công cụ tự động hóa tạo và đăng video ngắn lên YouTube Shorts, Twitter/X — có giao diện Web UI hiện đại, chạy hoàn toàn local.

> Yêu cầu **Python 3.12** và **Node.js 18+**

---

## Tính năng

- **YouTube Shorts** — Tự động tạo script, hình ảnh (Gemini AI), lồng tiếng (TTS), phụ đề, ghép video và upload lên YouTube
- **Twitter/X Bot** — Tạo nội dung bằng LLM và đăng bài tự động qua Selenium
- **Affiliate Marketing** — Scrape sản phẩm Amazon, tạo pitch bằng LLM, đăng lên Twitter
- **Outreach** — Scrape doanh nghiệp địa phương (Google Maps), tìm email và gửi email outreach tự động
- **Web UI** — Giao diện React quản lý toàn bộ workflow, xem gallery, theo dõi log real-time
- **CRON Jobs** — Lên lịch đăng bài tự động (1–3 lần/ngày)
- **Multi-account** — Quản lý nhiều tài khoản YouTube và Twitter song song

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
# Sao chép file cấu hình mẫu
copy config.example.json config.json
```

Mở `config.json` và điền các giá trị cần thiết (xem phần [Cấu hình](#cấu-hình) bên dưới).

**Bước 3:** Chạy setup tự động

```
setup.bat
```

Script sẽ tự động:
- Tạo Python virtual environment (`venv/`)
- Cài đặt tất cả Python dependencies (`requirements.txt`)
- Cài đặt npm packages cho frontend

### Thủ công (Windows/macOS/Linux)

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
.\venv\Scripts\activate

# Kích hoạt (macOS/Linux)
source venv/bin/activate

# Cài Python packages
pip install -r requirements.txt

# Cài frontend packages
cd frontend
npm install
cd ..
```

---

## Khởi chạy

### Windows

```
start_hub.bat
```

Sẽ mở 2 cửa sổ terminal:
- **Backend API** chạy tại `http://localhost:15001`
- **Frontend UI** chạy tại `http://localhost:5174`

Mở trình duyệt và truy cập: **http://localhost:5174**

### Thủ công

```bash
# Terminal 1 — Backend
cd src
..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload

# Terminal 2 — Frontend
cd frontend
npm run dev -- --port 5174
```

### Chạy CLI (không cần Web UI)

```bash
python src/main.py
```

### Chạy headless (CRON/scheduled)

```bash
python src/cron.py twitter <account_uuid> <ollama_model>
python src/cron.py youtube <account_uuid> <ollama_model>
```

---

## Cấu hình

Tất cả cấu hình nằm trong `config.json`. Các key quan trọng:

### LLM Backend

```json
"llm_backend": "ollama",
"ollama_base_url": "http://127.0.0.1:11434",
"ollama_model": "llama3:latest"
```

Hoặc dùng OpenAI-compatible API (LM Studio, OpenRouter...):

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
"tts_voice": "Jasper",
"tts_strict_mode": false
```

Các giọng hỗ trợ: `Jasper`, `Luna`, `Milo`, `Ava`, `Emma`

### Speech-to-Text (Subtitles)

```json
"stt_provider": "local_whisper",
"whisper_model": "base",
"whisper_device": "auto",
"whisper_compute_type": "int8"
```

Dùng AssemblyAI thay thế:

```json
"stt_provider": "assembly_ai",
"assembly_ai_api_key": "YOUR_KEY"
```

### Firefox Profile

```json
"firefox_profile": "ten-profile-firefox",
"headless": false
```

Profile Firefox phải đã đăng nhập sẵn YouTube và Twitter/X.

### Video & ImageMagick

```json
"imagemagick_path": "C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe",
"font": "bold_font.ttf",
"video_encode_preset": "veryfast",
"video_encode_crf": 24,
"threads": 2
```

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

## Cấu trúc thư mục

```
MoneyPrinter-short-video/
├── src/                    # Python backend
│   ├── api/                # FastAPI routes
│   │   ├── main.py         # App entry point, system endpoints
│   │   ├── youtube.py      # YouTube API routes
│   │   ├── twitter.py      # Twitter API routes
│   │   ├── affiliate.py    # Affiliate routes
│   │   ├── session_manager.py
│   │   └── log_stream.py   # SSE log streaming
│   ├── classes/            # Core workflow classes
│   │   ├── YouTube.py      # Video generation pipeline
│   │   ├── Twitter.py      # Tweet automation
│   │   ├── AFM.py          # Amazon affiliate
│   │   ├── Outreach.py     # Business outreach
│   │   └── Tts.py          # Text-to-speech wrapper
│   ├── config.py           # Config reader (ROOT_DIR-based)
│   ├── cache.py            # JSON persistence (.mp/)
│   ├── llm_provider.py     # Ollama/OpenAI client
│   ├── main.py             # CLI interactive menu
│   └── cron.py             # Headless scheduled runner
├── frontend/               # React + Vite + TypeScript UI
│   ├── src/
│   │   ├── App.tsx         # Main UI component
│   │   ├── index.css       # Global styles (Tailwind)
│   │   └── main.tsx        # React entry point
│   ├── package.json
│   └── vite.config.ts
├── fonts/                  # Font files cho subtitle overlay
├── Songs/                  # Background music
├── assets/                 # Static assets
├── scripts/                # Utility scripts
│   ├── preflight_local.py  # Kiểm tra dependencies
│   └── upload_video.sh     # Upload video tiện ích
├── .mp/                    # Runtime data (auto-generated)
│   └── sessions/           # Dữ liệu từng session video
├── config.json             # Cấu hình chính
├── config.example.json     # Cấu hình mẫu
├── requirements.txt        # Python dependencies
├── setup.bat               # Cài đặt lần đầu (Windows)
└── start_hub.bat           # Khởi chạy backend + frontend (Windows)
```

---

## API Endpoints

Backend chạy tại `http://localhost:15001`.

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/system/status` | Trạng thái hệ thống |
| GET | `/system/config` | Đọc config |
| PATCH | `/system/config` | Cập nhật config |
| GET | `/system/gallery` | Danh sách media files |
| GET | `/system/sessions` | Danh sách sessions |
| POST | `/system/sessions` | Tạo session mới |
| DELETE | `/system/sessions/{id}` | Xóa session |
| GET | `/system/logs/stream` | SSE log stream real-time |
| GET | `/system/llm/models` | Danh sách LLM models |
| GET | `/accounts/{platform}` | Danh sách accounts |
| POST | `/youtube/generate` | Bắt đầu tạo video |
| POST | `/twitter/post` | Đăng tweet |
| GET | `/media/*` | Serve media files |

---

## Quy trình tạo YouTube Short

1. **Script Setup** — Nhập chủ đề, LLM tạo kịch bản
2. **Generate Images** — Gemini AI tạo hình minh họa (9:16)
3. **Generate Audio** — KittenTTS chuyển text thành giọng nói
4. **Generate Subtitles** — Whisper/AssemblyAI tạo phụ đề SRT
5. **Compose Video** — MoviePy ghép hình + audio + phụ đề + nhạc nền
6. **Ready for Review** — Xem preview trong Web UI
7. **Published** — Upload lên YouTube qua Selenium

---

## Troubleshooting

**Lỗi "venv không tìm thấy":** Chạy `setup.bat` trước.

**Lỗi port đã được dùng:** `start_hub.bat` tự động kill process cũ trên port 15001 và 5174.

**Firefox không mở được:** Kiểm tra `firefox_profile` trong `config.json` — phải là tên profile đã tồn tại và đã đăng nhập.

**ImageMagick lỗi:** Đảm bảo `imagemagick_path` trỏ đúng đến `magick.exe`.

**Ollama không kết nối được:** Chạy `ollama serve` và kiểm tra `ollama_base_url`.

**Frontend không load:** Đợi vài giây sau khi chạy `start_hub.bat`, backend cần thời gian khởi động.

---

## License

Licensed under `Affero General Public License v3.0`. Xem [LICENSE](LICENSE) để biết thêm.

## Disclaimer

Project này chỉ dành cho mục đích học tập và nghiên cứu. Tác giả không chịu trách nhiệm về bất kỳ hành vi lạm dụng nào.
