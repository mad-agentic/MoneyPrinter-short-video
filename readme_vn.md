# MoneyPrinter — Tự Động Hóa Short Video Chỉ Với 1 Click

> **Từ ý tưởng đến video YouTube Short đã đăng — tự động 100%, chạy local, gần như miễn phí.**

MoneyPrinter là nền tảng tự động hóa chạy trên máy của bạn, biến **một ý tưởng** thành **video dọc hoàn chỉnh** rồi **đăng lên YouTube, Twitter/X, TikTok, Instagram** — tất cả từ một dashboard, chỉ với một nút bấm.

![Dashboard](docs/screenshots/1clickGeneratetovideo.png)

---

## Tại sao chọn MoneyPrinter?

Hầu hết tool "AI video" trên thị trường đều thu phí $30–$100/tháng, bắt buộc dùng cloud của họ, và bạn vẫn phải canh từng bước. MoneyPrinter khác hoàn toàn:

- **Chạy hoàn toàn trên máy bạn.** Không hóa đơn cloud, không phí mỗi lần render.
- **Không cần API trả phí.** Dùng Ollama local, KittenTTS, Whisper local — hoặc cắm vào bất kỳ endpoint OpenAI-compatible nào (9Router, LiteLLM, LM Studio) nếu muốn mạnh hơn.
- **1 click = full pipeline.** Research → Script → Ảnh → Giọng đọc → Phụ đề → Video → Upload. Không qua tab khác.
- **Đa nền tảng.** Compose một lần, đẩy lên YouTube Shorts, Twitter/X, TikTok, Instagram tự động.
- **Bạn vẫn là người kiểm soát.** Có cổng review thủ công trước khi đăng. Sửa bất kỳ bước nào, regenerate từng stage, session nào cũng resume được.

---

## Pipeline 1-Click

![Pipeline](docs/screenshots/Generatiom%20progress.png)

Chọn chủ đề. Bấm **Generate Short**. Xong.

| Stage | Công việc | Engine mặc định |
|---|---|---|
| 1. Research | Kéo trend và góc khai thác từ web | 9Router `tavily/search` |
| 2. Script | Viết script ngắn: hook → thân → CTA | Ollama / OpenAI-compatible |
| 3. Ảnh | Sinh ảnh 9:16 cho từng beat | Gemini image preview |
| 4. Giọng đọc | Đọc script theo ngôn ngữ/voice đã chọn | KittenTTS / Edge-TTS / Gemini TTS |
| 5. Phụ đề | Nghe audio và sinh caption `.srt` có timing | Whisper / Gemini STT |
| 6. Ghép video | Dựng MP4 1080×1920 có nhạc nền + caption | MoviePy + ImageMagick |
| 7. Đăng tải | Upload YouTube + cross-post mạng xã hội | Selenium automation |

Mỗi stage ghi vào session folder, nên nếu lỗi ở đâu bạn resume hoặc regenerate đúng chỗ đó — không mất công chạy lại từ đầu.

---

## Tính Năng Chi Tiết

### Workspace YouTube Shorts
![YouTube Workspace](docs/screenshots/Info%20Step123.png)

- Chọn **Custom Subject** + **Audio Language**
- Nút **Auto Build** viết nguyên script
- **Script Editor** sửa trực tiếp, có live preview
- **Draft CC** từ text + **Real CC** từ audio thật
- **Media Engine** gallery xem và swap ảnh thủ công
- **Generation Progress** panel với nút regenerate từng stage

### Research & Ideas Chat
![Research](docs/screenshots/Research.png)

Chat workspace research trend, brainstorm ý tưởng video, rồi **đẩy thẳng** ý tưởng hay nhất vào một YouTube session. Hết cảnh copy qua copy lại giữa các tab.

### Twitter/X Manager
![Twitter](docs/screenshots/Twitter.png)

- Quản lý nhiều tài khoản X
- Soạn + lên lịch post từ dashboard
- Xem lịch sử post theo từng account

### Affiliate CRM
![Affiliate](docs/screenshots/Afiliate.png)

- Scrape sản phẩm Amazon
- Auto-sinh pitch affiliate
- 1-click đẩy lên Twitter

### Cài Đặt Runtime + LLM
![LLM Settings](docs/screenshots/setting%20llm.png)
![Runtime Settings](docs/screenshots/setting%20runtime.png)

- Chọn backend LLM (Ollama, 9Router, OpenAI-compatible, custom proxy)
- Chọn model image / TTS / STT / search độc lập nhau
- Bật **fallback to local** để app không bao giờ kẹt vì thiếu key
- Tinh chỉnh FFmpeg CRF, profile trình duyệt, đường dẫn Firefox

---

## So Sánh Chi Phí

| Tool | Phí tháng | Local? | 1-click? |
|---|---|---|---|
| **MoneyPrinter** | **0₫** (hoặc tự host LLM) | ✅ | ✅ |
| OpusClip / Vizard | $30–$60/tháng | ❌ | một phần |
| Pictory / InVideo | $25–$75/tháng | ❌ | một phần |
| Dựng tay | "miễn phí" + 4 giờ/video | — | ❌ |

Bạn lo phần cứng (PC Windows + Python 3.12 + Firefox). Chúng tôi lo phần pipeline.

---

## Cài Đặt Nhanh (Windows)

Dung duong dan nay khi chi can chay app nhanh.

```powershell
# 1. Clone & vào thư mục
git clone https://github.com/mad-agentic/MoneyPrinter-short-video.git
cd MoneyPrinter-short-video

# 2. Copy config
copy config.example.json config.json

# 3. Cài mọi thứ (Python venv + npm)
setup.bat

# 4. Khởi động hub
start_hub.bat
```

Can huong dan setup day du? Doc [`docs/PROJECT_USAGE_VN.md`](docs/PROJECT_USAGE_VN.md).

Mở **http://localhost:5174** là chạy được luôn.

`start_hub.bat` kiểm tra port backend `15001` và frontend `5174` trước khi chạy. Nếu port đang bị process khác giữ, hãy tắt process đó hoặc đổi port trước khi mở hub.

> Backend API: `http://127.0.0.1:15001` · Frontend UI: `http://localhost:5174`

---

## Yêu Cầu Hệ Thống

| Dependency | Dùng để làm gì | Bắt buộc? |
|---|---|---|
| Python 3.12 | Backend + pipeline video | ✅ |
| Node.js 18+ | React frontend | ✅ |
| Firefox + Selenium profile | Auto upload YouTube / X | Khi muốn đăng tự động |
| ImageMagick 7.x | Render phụ đề | ✅ |
| FFmpeg | Encode audio/video | ✅ |
| Ollama **hoặc** bất kỳ endpoint OpenAI-compatible nào | LLM viết script | Ít nhất một |
| 9Router / Gemini API | Image + TTS + STT + search (khuyến nghị) | Không bắt buộc, có fallback local |

**Tối thiểu: 0 API key trả phí.** Mọi stage đều có local fallback.

---

## Đăng Đa Nền Tảng

Compose một lần. Đăng lên:

- **YouTube Shorts** — Selenium tự động, có lịch, có cổng review
- **Twitter/X** — auto-tweet cùng nội dung
- **TikTok + Instagram** — dùng qua PostBridge khi đã cấu hình `post_bridge.enabled`, API key, platforms và account IDs.
- **Affiliate links** — pitch sản phẩm Amazon auto-push lên X

---

## Tại Sao "Local-First" Lại Quan Trọng

- **Riêng tư.** Script, account, video chưa đăng không rời khỏi máy bạn.
- **Rẻ.** Không phí render, không seat license, không bill bất ngờ.
- **Nhanh.** Không upload lên cloud, không xếp hàng render.
- **Ổn định.** Không sợ "service temporarily unavailable" giữa pipeline.
- **Linh hoạt.** Thay bất kỳ model local, proxy, voice nào — chỉ qua config.

---

## Mục Lục Screenshots

| File | Mô tả |
|---|---|
| `1clickGeneratetovideo.png` | Workspace YouTube chính — 1-click generation |
| `Info Step123.png` | Script editor + audio text + language selector |
| `info step456.png` | CC draft, image engine, generation progress |
| `Generatiom progress.png` | Live pipeline progress + media gallery |
| `Research.png` | Chat workspace Research & Ideas |
| `Twitter.png` | Quản lý đa tài khoản Twitter/X |
| `Afiliate.png` | Affiliate CRM + product pitches |
| `setting llm.png` | LLM backend + chọn model |
| `setting runtime.png` | Runtime + browser + encoding |

---

## Checklist Setup Day Du

1. Cai truoc cac dependency:
   - Python 3.12
   - Node.js 18+
   - FFmpeg
   - ImageMagick 7.x
   - Firefox neu muon auto upload YouTube/X
2. Copy `config.example.json` thanh `config.json`.
3. Mo `config.json`, set toi thieu:
   - `imagemagick_path`
   - LLM provider, vi du Ollama hoac OpenAI-compatible/9Router
   - image, TTS, STT, search model neu dung provider routing
4. Chay `setup.bat` mot lan de tao venv Python va cai frontend package.
5. Chay `start_hub.bat` khi dung hang ngay.
6. Mo `http://localhost:5174`.
7. Vao Settings kiem tra provider, model, voice, ImageMagick, FFmpeg, browser path truoc khi generate/upload.

Manual review la che do mac dinh. Chi bat auto publish sau khi da kiem tra account path, metadata va video output.

Lenh debug rieng tung phan:

```powershell
# Backend only
cd src
..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload

# Frontend only
cd frontend
npm run dev -- --host 127.0.0.1 --port 5174
```

Khong commit file runtime local: `config.json`, `.env`, `.mp/`, browser profile, media output, `venv/`, `frontend/node_modules/`.

---

## License

MIT — tự lo model, tự lo proxy, tự lo workflow. Dùng thoải mái.
