# MoneyPrinter Short Video

MoneyPrinter là dashboard local-first để nghiên cứu ý tưởng, viết script, tạo ảnh, tạo giọng đọc, tạo phụ đề, ghép video dọc và chuẩn bị YouTube Shorts trước khi đăng.

- Bản tiếng Anh: [README.md](README.md)
- Backend API: `http://127.0.0.1:15001`
- Frontend UI: `http://localhost:5174`

> Môi trường khuyến nghị: Windows, Python 3.12, Node.js 18+, Firefox, ImageMagick 7.x.

---

## Ảnh giao diện

| YouTube workflow | Research & Ideas |
|---|---|
| ![YouTube workflow](docs/screenshots/1.png) | ![Research workspace](docs/screenshots/2.png) |

| Cấu hình 9Router | Session và Media Engine |
|---|---|
| ![9Router settings](docs/screenshots/3.png) | ![Session media](docs/screenshots/4.png) |

| Review trước khi đăng |
|---|
| ![Final review](docs/screenshots/5.png) |

---

## Công cụ này làm gì?

MoneyPrinter biến một chủ đề hoặc ý tưởng research thành một video dọc hoàn chỉnh:

1. Research trend hoặc nhập topic thủ công.
2. Tạo và chỉnh script ngắn.
3. Tạo image prompt và ảnh 9:16.
4. Tạo audio bằng TTS local hoặc 9Router.
5. Nghe audio và tạo phụ đề `.srt` bằng STT.
6. Ghép video 1080x1920 với ảnh, voice, nhạc nền và caption.
7. Lưu output vào session để review.
8. Có thể đăng YouTube hoặc cross-post sang social khi đã duyệt.

Mỗi lần chạy được lưu trong `.mp/sessions/<session-folder>/`, nên có thể resume hoặc regenerate từ một stage cụ thể.

---

## Tính năng chính

| Khu vực | Mô tả |
|---|---|
| YouTube Shorts | Tạo topic, script, metadata, ảnh, TTS, phụ đề, ghép video, review và upload. |
| Research & Ideas | Workspace chat để research, tạo ý tưởng video và đẩy sang YouTube session. |
| 9Router | Một lớp provider cho chat, image, TTS, STT, web search và fetch model. |
| Local fallback | Ollama, KittenTTS, local Whisper, Gemini image API, AssemblyAI/OmniVoice tùy chọn. |
| Session manager | Danh sách session, badge stage, resume state, dễ dọn session duplicate lỗi. |
| Media Engine | Gallery theo session, chọn ảnh thủ công, tái sử dụng ảnh khi regenerate. |
| Subtitle preview | Draft CC từ text và CC thật sinh từ audio. |
| Manual review | Generate video trước, kiểm tra metadata/video, rồi mới publish. |
| Twitter/X và affiliate | Workspace phụ cho đăng Twitter và tạo pitch affiliate. |

---

## Yêu cầu hệ thống

| Dependency | Dùng để làm gì |
|---|---|
| Python 3.12 | Backend API và pipeline video. |
| Node.js 18+ | React/Vite frontend. |
| Firefox | Selenium upload automation. |
| ImageMagick 7.x | Render text/phụ đề bằng MoviePy. |
| FFmpeg | Encode audio/video qua MoviePy. |
| Ollama hoặc OpenAI-compatible API | LLM để viết script, metadata, dịch. |
| 9Router hoặc Gemini API | Provider cloud cho chat, ảnh, TTS, STT và search. |

---

## Cài đặt nhanh trên Windows

1. Copy file cấu hình mẫu:

```bat
copy config.example.json config.json
```

2. Mở `config.json` và cấu hình tối thiểu:

```json
{
  "imagemagick_path": "C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe",
  "llm_backend": "openai_compatible",
  "openai_base_url": "http://localhost:20128/v1",
  "openai_model": "cx/gpt-5.5",
  "openai_api_key": "none"
}
```

3. Cài dependencies:

```bat
setup.bat
```

4. Chạy hub:

```bat
start_hub.bat
```

5. Mở trình duyệt:

```text
http://localhost:5174
```

---

## Chạy thủ công

Backend:

```powershell
cd src
..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload
```

Frontend:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5174
```

Build frontend production:

```powershell
cd frontend
npm run build
```

---

## Cấu hình 9Router khuyến nghị

Mở Settings trong UI và cấu hình phần 9Router. Các giá trị này nằm trong `providers.ninerouter` của `config.json`.

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
    "tts_response_format": "wav",
    "stt_model": "gemini/gemini-2.5-flash",
    "stt_response_format": "srt",
    "search_model": "search-combo"
  }
}
```

### Các model dùng để làm gì?

| Setting | Công dụng | Ghi chú |
|---|---|---|
| Chat model | Viết idea, script, metadata, dịch, pitch affiliate. | Ví dụ `cx/gpt-5.5`. |
| Image model | Tạo ảnh dọc cho video. | Nên dùng model hỗ trợ 9:16. |
| TTS model | Đọc script thành audio. | Gemini TTS dùng voice kiểu `Zephyr`; Edge TTS dùng voice theo locale. |
| TTS voice | Giọng đọc bên trong TTS model. | UI tách voice tiếng Anh và tiếng Việt. |
| STT model | Nghe audio và tạo phụ đề. | STT không tạo giọng, chỉ tạo caption. |
| Search model | Research trend/web. | Mặc định `search-combo`. |

---

## Hướng dẫn chọn voice

Chọn language và voice trong YouTube workspace cho từng video.

### Tiếng Anh

Voice khuyến nghị:

- `Luna`
- `Ava`
- `Emma`

Cấu hình thường dùng:

```text
TTS Model: gemini/gemini-2.5-flash-preview-tts
TTS Voice: Luna
STT Model: gemini/gemini-2.5-flash hoặc gemini/gemini-2.5-pro
```

### Tiếng Việt

Voice khuyến nghị:

- `vi-VN-HoaiMyNeural` - giọng nữ tiếng Việt, mặc định.
- `vi-VN-NamMinhNeural` - giọng nam tiếng Việt.

Cấu hình thường dùng:

```text
TTS Model: edge-tts/vi-VN-HoaiMyNeural
TTS Voice: vi-VN-HoaiMyNeural
STT Model: gemini/gemini-2.5-flash hoặc gemini/gemini-2.5-pro
```

Backend có guardrail: nếu video tiếng Việt nhưng request gửi voice tiếng Anh như `Luna`, API sẽ tự đổi về `vi-VN-HoaiMyNeural`.

---

## Workflow tạo YouTube Short

1. Chọn hoặc thêm YouTube account.
2. Nhập Custom Subject.
3. Bấm Auto Build để tạo Audio Text.
4. Review và chỉnh script.
5. Chọn Audio Language và TTS Voice.
6. Tạo Draft CC hoặc Gen Whisper CC từ audio thật.
7. Chọn manual review hoặc auto publish.
8. Bấm Generate Short.
9. Kiểm tra video, title, description, tags.
10. Bấm Push to YouTube khi đã sẵn sàng.

### Regenerate từng stage

Panel Generation Progress cho phép chạy lại từng bước:

- Script setup
- Generate images
- Generate audio
- Generate subtitles
- Compose video
- Ready for review

Nếu muốn dùng ảnh tự chọn, chọn ảnh trong Media Engine trước rồi chạy Custom Step.

---

## Session lưu ở đâu?

Mỗi session nằm trong:

```text
.mp/sessions/<session-folder>/
```

Cấu trúc thường gặp:

```text
session.json          # Metadata, stage hiện tại, path audio/video
audio/                # Audio TTS và file phụ đề
images/               # Ảnh sinh ra hoặc ảnh tự chọn
video/                # MP4 cuối cùng
```

Nếu bị duplicate session, giữ session có `subject`, `script`, `video_path` thật. Session lỗi thường đang `init`, rỗng subject/script/video và có thể xóa an toàn sau khi kiểm tra.

---

## Biến môi trường

App chủ yếu đọc `config.json`. File `.env` không được mọi entry point tự load nếu launcher/process chưa nạp nó.

| Biến | Dùng để làm gì |
|---|---|
| `GEMINI_API_KEY` | Fallback cho Gemini/Nano Banana image API khi config key trống. |
| `GH_TOKEN` | Có thể được webdriver-manager dùng gián tiếp để tránh GitHub rate limit. |
| `HF_TOKEN` | App không gọi trực tiếp; thư viện model có thể tự đọc nếu cần. |
| `OPENAI_API_KEY` | Fallback cho OpenAI-compatible provider nếu cấu hình dùng. |

Không commit secret thật. Nếu token từng lộ trong chat, log, screenshot hoặc commit, hãy rotate/revoke.

---

## Xử lý lỗi thường gặp

### `Unexpected UTF-8 BOM`

Nên lưu JSON bằng UTF-8 without BOM. Backend hiện đã tolerant BOM với `config.json`, nhưng một số tool như `python -m json.tool` vẫn có thể báo lỗi.

### `JSONDecodeError: Expecting value: line 1 column 1`

Thường do `config.json` rỗng, sai JSON, hoặc BOM bị đọc bởi code path chưa tolerant. Kiểm tra bằng:

```powershell
python -m json.tool config.json
```

### Subtitle equalizer lỗi hoặc video không có phụ đề

Một số STT provider trả plain transcript thay vì SRT thật. Pipeline YouTube hiện sẽ convert transcript text sang SRT timed nếu có thể, hoặc bỏ overlay phụ đề một cách an toàn nếu không có caption render được.

### ImageMagick render lỗi

Kiểm tra `imagemagick_path` trỏ đúng file `magick.exe`:

```json
"imagemagick_path": "C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"
```

### Firefox automation lỗi

Kiểm tra Firefox đã cài và profile trong config tồn tại. Upload tự động cần profile đã đăng nhập YouTube/Twitter.

### Fetch Voices trên 9Router bị unauthorized

Kiểm tra `providers.ninerouter.api_key` và auth mode của server 9Router. Khi endpoint list voice không dùng được, vẫn có thể nhập voice thủ công.

---

## Ghi chú phát triển

| Path | Vai trò |
|---|---|
| `src/api/main.py` | FastAPI app, config endpoint, model/voice listing endpoint. |
| `src/api/youtube.py` | API tạo video, CC preview, background generation. |
| `src/classes/YouTube.py` | Pipeline video chính. |
| `src/classes/Tts.py` | TTS abstraction và fallback. |
| `src/providers/ninerouter.py` | Client cho 9Router. |
| `frontend/src/App.tsx` | Dashboard chính. |
| `docs/skills/` | Skill packs cho Codex/MoneyPrinter. |
| `docs/screenshots/` | Ảnh dùng trong README. |

Lệnh kiểm tra nhanh:

```powershell
venv\Scripts\python.exe -m py_compile src\api\main.py src\api\youtube.py src\classes\YouTube.py src\classes\Tts.py
cd frontend
npm run build
```

---

## Bảo mật

- Không đưa API key vào screenshot, commit, log public.
- Dùng field password/masked khi chụp Settings.
- Kiểm tra `.env`, `config.json`, browser profile trước khi share project.
- Thư mục `.mp/` có thể chứa script riêng, tên account, video output và metadata nhạy cảm.

---

## License

Sử dụng theo license của project và điều khoản của các provider/model/browser automation/media asset mà bạn cấu hình.
