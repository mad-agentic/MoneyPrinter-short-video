# Hướng dẫn sử dụng MoneyPrinter Short Video

Tài liệu này dùng cho người chạy project ở máy local trên Windows. Mục tiêu: cài đúng, cấu hình đúng, chạy app ổn định, tạo video ngắn theo workflow chuẩn, và biết xử lý các lỗi thường gặp.

## 1. Project này dùng để làm gì

MoneyPrinter Short Video là app local-first để tạo nội dung video ngắn. App có backend Python/FastAPI, frontend React/Vite, và dữ liệu runtime nằm trong thư mục `.mp/`.

Các việc chính app hỗ trợ:

- Research ý tưởng video.
- Viết script ngắn.
- Tạo prompt ảnh và ảnh dọc 9:16.
- Tạo giọng đọc bằng TTS.
- Tạo phụ đề bằng STT.
- Ghép video dọc 1080x1920.
- Review video trước khi đăng.
- Upload YouTube Shorts nếu cấu hình account đúng.
- Hỗ trợ thêm Twitter/X, affiliate, outreach, media gallery.

URL mặc định:

- Backend API: `http://127.0.0.1:15001`
- Frontend UI: `http://localhost:5174`

## 2. Yêu cầu máy

Cài trước các phần sau:

- Windows.
- Python 3.12.
- Node.js 18 hoặc mới hơn.
- Firefox, dùng cho workflow upload bằng browser automation.
- ImageMagick 7.x, dùng để render text/phụ đề qua MoviePy.
- FFmpeg, dùng để encode audio/video.
- Một provider LLM/TTS/image/STT, ví dụ 9Router, Ollama, Gemini, hoặc OpenAI-compatible API.

Khuyến nghị dùng 9Router nếu muốn gom chat, image, TTS, STT, search vào một nơi.

## 3. Cài đặt lần đầu

Mở PowerShell tại thư mục project:

```powershell
cd C:\Users\admin\Desktop\_AI\MoneyPrinter-short-video
```

Copy file cấu hình mẫu:

```powershell
copy config.example.json config.json
```

Cài dependency backend và frontend:

```powershell
setup.bat
```

Sau khi setup xong, không commit các file local như `config.json`, `.env`, `.mp/`, `venv/`, `frontend/node_modules/`.

## 4. Cấu hình tối thiểu

Mở `config.json`, chỉnh ít nhất các phần sau.

### ImageMagick

Đường dẫn thường gặp trên Windows:

```json
"imagemagick_path": "C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"
```

Nếu cài ImageMagick ở nơi khác, trỏ đúng tới `magick.exe`.

### Provider AI khuyến nghị: 9Router

Cấu hình mẫu:

```json
{
  "llm_backend": "openai_compatible",
  "openai_base_url": "http://localhost:20128/v1",
  "openai_model": "cx/gpt-5.5",
  "openai_api_key": "none",
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
      "search_model": "tavily/search",
      "search_max_results": 10
    }
  }
}
```

Ý nghĩa model:

| Setting | Dùng cho | Ghi chú |
|---|---|---|
| `chat_model` | Viết ý tưởng, script, metadata, dịch, affiliate pitch | Nên dùng model viết tốt. |
| `image_model` | Tạo ảnh dọc theo scene | Nên dùng model hỗ trợ 9:16. |
| `tts_model` | Đọc script thành audio | Edge TTS hoặc Gemini TTS. |
| `tts_voice` | Giọng đọc | Chọn đúng ngôn ngữ video. |
| `stt_model` | Nghe audio tạo phụ đề | STT không tạo giọng, chỉ tạo caption. |
| `search_model` | Research web/trend | Mặc định `tavily/search`. |

### Voice tiếng Việt

Khuyến nghị:

```text
TTS Model: edge-tts/vi-VN-HoaiMyNeural
TTS Voice: vi-VN-HoaiMyNeural
STT Model: gemini/gemini-2.5-flash
```

Voice khác:

- `vi-VN-HoaiMyNeural`: nữ, tiếng Việt.
- `vi-VN-NamMinhNeural`: nam, tiếng Việt.

### Voice tiếng Anh

Khuyến nghị:

```text
TTS Model: gemini/gemini-2.5-flash-preview-tts
TTS Voice: Luna
STT Model: gemini/gemini-2.5-flash
```

Voice thường dùng:

- `Luna`
- `Ava`
- `Emma`

Không dùng voice tiếng Anh cho video tiếng Việt. Backend có fallback về `vi-VN-HoaiMyNeural`, nhưng tốt nhất vẫn chọn đúng trong UI.

## 5. Chạy app

Cách chuẩn:

```powershell
start_hub.bat
```

Sau đó mở:

```text
http://localhost:5174
```

Nếu muốn chạy từng phần để debug:

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

## 6. Workflow tạo YouTube Short chuẩn

Làm theo thứ tự này để ít lỗi nhất:

1. Mở app tại `http://localhost:5174`.
2. Vào Settings, kiểm tra provider, model, voice, ImageMagick.
3. Vào YouTube workspace.
4. Chọn hoặc thêm YouTube account.
5. Nhập `Custom Subject` rõ ràng, ví dụ: `5 mẹo tiết kiệm tiền cho dân văn phòng Việt Nam`.
6. Bấm Auto Build để tạo script/audio text.
7. Đọc lại script, xóa mọi stage direction không nên đọc thành tiếng.
8. Chọn `Audio Language` đúng với script.
9. Chọn TTS voice đúng ngôn ngữ.
10. Tạo draft caption nếu cần xem trước nội dung.
11. Chạy Generate Short.
12. Chờ pipeline tạo ảnh, audio, subtitle, video.
13. Mở video output để review.
14. Kiểm tra title, description, tags.
15. Chỉ upload khi video và metadata đã đúng.

Nguyên tắc an toàn: bật manual review. Không auto publish khi chưa xem video.

## 7. Workflow Research & Ideas

Dùng khi chưa có topic rõ.

1. Mở Research & Ideas.
2. Nhập chủ đề/ngách muốn tìm ý tưởng.
3. Để research engine tổng hợp nguồn và đề xuất idea.
4. Chọn idea có hook rõ, có audience rõ, có thể làm video ngắn.
5. Prefill idea sang YouTube session.
6. Quay lại workflow YouTube Short ở bước review script.

Prompt research nên cụ thể:

```text
Tìm 10 ý tưởng YouTube Shorts tiếng Việt về tài chính cá nhân cho người mới đi làm. Ưu tiên hook gây tò mò, nội dung có thể nói trong 45 giây.
```

## 8. Workflow Media Engine

Dùng khi muốn kiểm soát ảnh thay vì để app tự chọn toàn bộ.

1. Mở session muốn chỉnh.
2. Vào Media Engine hoặc gallery của session.
3. Chọn ảnh muốn dùng lại.
4. Regenerate stage cần thiết, thường là compose video.
5. Kiểm tra video mới.

Không xóa thủ công file trong `.mp/sessions/` khi app đang chạy.

## 9. Workflow Twitter/X, Affiliate, Outreach

Các workspace này là phụ trợ cho nội dung và phân phối.

Twitter/X:

- Thêm account đúng profile/browser state.
- Generate post từ topic hoặc video idea.
- Review text trước khi post.

Affiliate:

- Dùng để tạo pitch, CRM affiliate, hoặc nội dung outreach.
- Luôn kiểm tra link, tên sản phẩm, claim, giá, điều khoản affiliate trước khi gửi.

Outreach/email:

- Cấu hình SMTP trong `config.json` nếu dùng gửi email.
- Không commit username/password SMTP.

## 10. Session và file output

Mỗi lần tạo video sẽ nằm trong:

```text
.mp/sessions/<session-folder>/
```

Các file thường gặp:

```text
session.json          # Metadata session, stage hiện tại, subject, script, path output
audio/                # Audio TTS và subtitle
images/               # Ảnh generate hoặc ảnh đã chọn
video/                # MP4 cuối cùng
```

Nếu thấy session duplicate, giữ session có subject/script/video path thật. Session trống kiểu `init` có thể là session lỗi hoặc session nháp.

## 11. Những thứ không được commit hoặc chia sẻ

Không commit, không upload public:

- `.env`
- `config.json`
- `.mp/`
- Browser profiles.
- Cookies, tokens, API keys.
- Video/audio/image output đã generate.
- `venv/`
- `frontend/node_modules/`
- Build/cache folders.

Dùng `config.example.json` để lưu default và ví dụ cấu hình.

## 12. Kiểm tra project khi sửa code

Backend Python:

```powershell
python -m py_compile src\config.py src\llm_provider.py src\research_engine.py
```

API hoặc YouTube workflow:

```powershell
python -m py_compile src\api\main.py src\api\youtube.py src\classes\YouTube.py
```

TTS hoặc voice:

```powershell
python -m py_compile src\config.py src\api\main.py src\api\youtube.py src\classes\Tts.py src\classes\YouTube.py
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Skill package:

```powershell
python scripts\package_skills.py --skill <skill-name>
```

## 13. Xử lý lỗi thường gặp

### Lỗi `Invalid JSON body`

Ví dụ:

```json
{"error":{"message":"Invalid JSON body","type":"invalid_request_error","code":"bad_request"}}
```

Ý nghĩa: request gửi tới API/provider có body JSON sai format. Đây không phải lỗi API key sai.

Cách xử lý:

1. Xem terminal backend ngay trước dòng lỗi.
2. Kiểm tra request đang gọi provider nào: chat, image, TTS, STT, search.
3. Kiểm tra prompt/script có dấu nháy kép chưa escape, ký tự lạ, JSON copy từ AI bị thiếu ngoặc, hoặc trailing comma.
4. Kiểm tra `config.json` bằng lệnh:

```powershell
python -m json.tool config.json
```

5. Nếu lỗi xuất hiện sau khi chỉnh Settings trong UI, mở lại `config.json` và so sánh với `config.example.json`.
6. Không paste raw JSON hỏng vào prompt/model field. Model field chỉ nên là text như `cx/gpt-5.5`, không phải object JSON.

### Lỗi `JSONDecodeError`

Thường do `config.json` rỗng, sai format, hoặc encoding lỗi.

Chạy:

```powershell
python -m json.tool config.json
```

Nếu lỗi, copy lại từ `config.example.json`, rồi chỉnh từng phần.

### ImageMagick render subtitle lỗi

Kiểm tra:

```json
"imagemagick_path": "C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe"
```

Nếu path sai, MoviePy có thể không render caption được.

### Video không có phụ đề

Nguyên nhân thường gặp:

- STT provider trả transcript text thay vì SRT.
- Audio lỗi hoặc quá ngắn.
- Subtitle file rỗng.
- ImageMagick lỗi render text.

Xử lý:

1. Regenerate subtitles từ audio thật.
2. Kiểm tra file trong `.mp/sessions/<session>/audio/`.
3. Xem log backend để biết STT provider trả gì.

### Firefox upload lỗi

Kiểm tra:

- Firefox đã cài chưa.
- Profile Firefox có tồn tại không.
- Profile đã đăng nhập YouTube/Twitter chưa.
- Không chạy nhiều browser automation cùng lúc trên cùng profile.

### 9Router voice list unauthorized

Kiểm tra:

- `providers.ninerouter.enabled` là `true`.
- `ai_provider.active` là `ninerouter`.
- `providers.ninerouter.base_url` đúng.
- `providers.ninerouter.api_key` đúng với server auth mode.

Nếu endpoint voice list lỗi, vẫn có thể nhập voice thủ công nếu provider hỗ trợ.

### Backend hoặc frontend không lên

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

Nếu port bận, đổi port frontend, nhưng backend mặc định vẫn là `15001`.

## 14. Quy trình dùng hằng ngày

Checklist ngắn:

1. Chạy `start_hub.bat`.
2. Mở `http://localhost:5174`.
3. Kiểm tra Settings nếu vừa đổi provider/model.
4. Research idea hoặc nhập topic thủ công.
5. Generate script.
6. Review script.
7. Chọn language/voice.
8. Generate Short.
9. Review video trong session.
10. Upload hoặc cross-post sau khi đã kiểm tra.

## 15. Quy tắc nội dung trước khi publish

Trước khi đăng video:

- Script không có stage direction như `(pause)`, `[music]`, `Narrator:` nếu TTS sẽ đọc thành tiếng.
- Title không quá dài và không sai nội dung.
- Description không chứa placeholder.
- Tags liên quan tới nội dung.
- Voice đúng ngôn ngữ.
- Caption khớp audio.
- Video không dùng ảnh sai context, ảnh lỗi mặt/tay/text, hoặc ảnh có watermark không mong muốn.
- Không publish tự động nếu chưa xem video output.

## 16. Ghi nhớ quan trọng

- `config.json` là cấu hình local, không commit.
- `.mp/` là dữ liệu runtime, không coi là source code.
- Muốn sửa logic provider, dùng `src/providers/` và `src/llm_provider.py`, không gọi API trực tiếp từ feature code.
- Muốn sửa config, dùng helper trong `src/config.py`, không đọc `config.json` trực tiếp trong business logic mới.
- Khi sửa TTS voice/model, phải giữ đồng bộ giữa config, API, UI, và `src/classes/Tts.py`.
