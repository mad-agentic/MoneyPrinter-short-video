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

### OmniVoice local presets

OmniVoice trong app khong dung voice ID co dinh nhu Edge TTS. UI hien preset, backend chuyen preset thanh `instruct` de model tao chat giong.

English presets:

- `EN Nova`: female, young adult, high pitch, american accent
- `EN Kai`: male, young adult, moderate pitch, american accent
- `EN Sage`: male, elderly, low pitch, british accent
- `EN Vera`: female, middle-aged, moderate pitch, british accent
- `EN Orion`: male, middle-aged, low pitch, american accent
- `EN Iris`: female, child, high pitch, american accent
- `EN Atlas`: male, young adult, high pitch, british accent
- `EN Breeze`: female, young adult, whisper, american accent

Vietnamese-first presets:

- `VI Hoai`: female, young adult, moderate pitch
- `VI Minh`: male, young adult, moderate pitch
- `VI Linh`: female, middle-aged, low pitch
- `VI Thoai`: male, middle-aged, low pitch
- `VI An`: female, young adult, high pitch
- `VI Nam`: male, young adult, high pitch
- `VI Thao`: female, elderly, low pitch
- `VI Bao`: male, elderly, low pitch

Muon custom voice rieng, sua `omnivoice_instruct` trong `config.json`. Khi field nay co gia tri, backend uu tien no hon preset. Nguon check:

- https://github.com/k2-fsa/OmniVoice
- https://pypi.org/project/omnivoice/

Không dùng voice tiếng Anh cho video tiếng Việt. Backend có fallback về `vi-VN-HoaiMyNeural`, nhưng tốt nhất vẫn chọn đúng trong UI.

## 5. Chạy app

Cách chuẩn:

```powershell
start_hub.bat
```

Luu y: `start_hub.bat` se kiem tra port `15001` va `5174`. Neu port dang bi process khac giu, script co the dung process do truoc khi mo backend/frontend moi. Neu dang chay service quan trong tren hai port nay, hay tat thu cong hoac doi port truoc.

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

Manual review la che do mac dinh. Chi bat auto publish sau khi da kiem tra account path, metadata va video output.

### Them YouTube account trong dashboard

Trong popup **Add YouTube Account**, dien nhu sau:

1. `Nickname *`: ten de nho cho account, vi du `mad-youtube`, `finance-main`, `shorts-vn`.
2. `Niche *`: chu de/ngach cua kenh, vi du `kiem tien online`, `motivation`, `tech AI`, `finance`.
3. `Firefox Profile Path`: chi can dien neu muon app tu upload bang Selenium. Neu chi generate video, co the de trong.
4. `Language`: ngon ngu mac dinh cua kenh/script, vi du `vietnamese` hoac `english`.

Cach lay `Firefox Profile Path`:

1. Mo Firefox va dang nhap san YouTube/YouTube Studio bang account muon upload.
2. Go `about:profiles` tren thanh dia chi Firefox.
3. Tim profile dang dung, copy dong `Root Directory`.
4. Dan path do vao o `Firefox Profile Path`.

Vi du:

```text
C:\Users\MAD\AppData\Roaming\Mozilla\Firefox\Profiles\abc123.default-release
```

Luu y: nut **Add Account** khong dang nhap YouTube cho ban. No chi luu account vao runtime cache `.mp/youtube.json`. Profile Firefox phai da dang nhap san neu muon upload tu dong.

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

### Loi 9Router model sai capability

Vi du:

```text
Provider 'codex' does not support STT
Unknown provider: search-combo
```

Y nghia: model/provider dang chon khong ho tro dung chuc nang. Chat model khong dung thay cho STT/TTS/search duoc neu 9Router khong map capability do.

Cach xu ly:

1. Voi search, dung `providers.ninerouter.search_model = "tavily/search"` hoac model co trong `/v1/models/web`.
2. Voi STT, dung model co trong `/v1/models/stt`; neu chua chac, dat `stt_provider = "local_whisper"`.
3. Voi TTS, dung model co trong `/v1/models/tts`; tieng Viet nen dung `edge-tts/vi-VN-HoaiMyNeural` neu server ho tro.
4. Khong dien chat model nhu `cx/gpt-5.5` vao `stt_model` hoac `tts_model` tru khi `/v1/models/stt` hoac `/v1/models/tts` liet ke dung model do.

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

## 14. Runtime Settings trong dashboard

Bang nay giai thich cac field trong panel **Runtime Settings**. Sau khi sua, bam **Save**. Neu thay backend/frontend van dung cau hinh cu, restart `start_hub.bat`.

| Setting tren UI | Key trong `config.json` | Tac dung | Goi y nhanh |
|---|---|---|---|
| `Verbose logs` | `verbose` | In log chi tiet hon trong terminal/backend. | Bat khi debug loi, tat khi chay binh thuong cho gon log. |
| `Headless browser` | `headless` | Chay automation browser khong mo cua so Firefox. | Tat khi can xem upload/browser lam gi; bat khi may da on dinh. |
| `TTS strict mode` | `tts_strict_mode` | Neu TTS loi mot phan thi fail ca run thay vi tiep tuc voi audio thieu. | Bat khi can video sach; tat khi muon pipeline tiep tuc de test. |
| `Default is for kids` | `is_for_kids` | Flag audience mac dinh khi upload YouTube. | Thuong de tat, tru khi kenh/video lam cho tre em. |
| `Threads` | `threads` | So worker/luong cho render va mot so viec song song. Image generation bi clamp toi da 4 trong pipeline. | 2-4 on dinh; cao qua de gap rate-limit/timeout. |
| `TTS engine` | `tts_engine` | Engine doc text thanh audio. | `omnivoice` chat luong cao can GPU; `kitten` nhanh/local; `ninerouter` dung cloud 9Router. |
| `TTS fallback engine` | `tts_fallback_engine` | Engine du phong neu TTS chinh loi. | Nen khac engine chinh neu muon co fallback that. Neu chinh la `omnivoice`, fallback `kitten` hoac `ninerouter` se an toan hon. |
| `TTS voice` | `tts_voice` | Giong doc mac dinh cho TTS. | Chon voice dung ngon ngu script. Voi OmniVoice, preset duoc doi thanh `instruct`. |
| `STT provider` | `stt_provider` | Engine nghe audio de tao subtitle/caption. | `local_whisper` mien phi/local; `whisperx` can dependency rieng; `ninerouter` dung cloud; `third_party_assemblyai` can API key. |
| `Whisper model` | `whisper_model` | Kich co model Whisper cho subtitle. | `tiny/base` nhanh, kem hon; `small` can bang; `medium` tot hon nhung cham. |
| `Whisper device` | `whisper_device` | Thiet bi chay Whisper. | `auto` thu GPU roi fallback; `cpu` on dinh; `cuda` nhanh neu GPU/driver OK. |
| `Whisper compute type` | `whisper_compute_type` | Do chinh xac/toc do tinh toan Whisper. | `int8` nhanh va nhe tren CPU; `float16` hop GPU; `float32` nang hon. |
| `Whisper VAD filter` | `whisper_vad_filter` | Loc im lang/tieng on truoc khi transcribe. | Bat khi audio co im lang/noise; tat neu subtitle bi mat chu hoac muon nhanh. |
| `Whisper beam size` | `whisper_beam_size` | Do rong search khi decode subtitle. | `1` nhanh; `2-3` tot hon nhung cham; toi da UI la 5. |
| `Title audio intro` | `enable_title_audio` | Doc subject/title o dau video truoc noi dung chinh. | Bat neu muon intro ro chu de; tat neu muon vao thang hook. |
| `Video preset` | `video_encode_preset` | Preset x264/FFmpeg, anh huong toc do encode. | `veryfast` can bang; `ultrafast/superfast` nhanh hon nhung file/quality kem hon; `medium` cham hon. |
| `Video CRF (18-35)` | `video_encode_crf` | Chat luong nen video. So thap = dep hon/file lon hon; so cao = nhe hon/xau hon. | 20-24 dep/on dinh; 24-28 nhanh va nhe hon. |
| `Script sentence length` | `script_sentence_length` | So cau muc tieu trong block script generate. | 3-5 hop YouTube Shorts; tang neu muon script dai hon moi block. |
| `Subtitle font file` | `font` | Font dung de render subtitle qua MoviePy/ImageMagick. | Chon file trong folder fonts. Neu subtitle loi, kiem tra font va `imagemagick_path`. |

Luu y rieng cho OmniVoice:

- `tts_voice` la preset UI, khong phai voice ID server co dinh.
- `omnivoice_instruct` neu co gia tri se override preset voice.
- Audio dai duoc app chia thanh chunk ngan va reset seed truoc moi chunk de giam lech giong. Khong dung OmniVoice long-form vi co the dung o buoc `model.generate()` tren mot so may.
- Neu chon `vi_female_ref`, `vi_male_ref`, hoac `en_female_ref`, backend se dung `ref_audio` + `ref_text` tu `assets/omnivoice_refs/voices.json` cho moi chunk trong cung video. Cach nay on dinh voice hon preset instruct.

### OmniVoice reference voices

Tao 3 voice ref synthetic mac dinh:

```powershell
uv run python scripts\omnivoice_refs.py create-defaults
```

Lenh nay tao:

```text
assets/omnivoice_refs/vi_female_ref.wav
assets/omnivoice_refs/vi_male_ref.wav
assets/omnivoice_refs/en_female_ref.wav
assets/omnivoice_refs/voices.json
```

Kiem tra danh sach:

```powershell
uv run python scripts\omnivoice_refs.py list
```

Test mot voice:

```powershell
uv run python scripts\omnivoice_refs.py test vi_female_ref
```

Sau khi tao refs, vao dashboard chon:

```text
TTS engine = omnivoice
TTS voice = vi_female_ref | vi_male_ref | en_female_ref
```

Log khi chay dung ref se co:

```text
OmniVoice reference voice active (vi_female_ref)
OmniVoice chunk 1/3 started (... chars)
```

Neu chua tao file `.wav`, backend se fallback ve preset/instruct cua OmniVoice va voice co the van lech giua chunks.

## 15. Quy trình dùng hằng ngày

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

## 16. Quy tắc nội dung trước khi publish

Publish state nen dung thong nhat:

- `ready_for_review`: video da render, chua upload.
- `published`: upload thanh cong.
- `publish_failed`: upload loi, co the retry.
- `publish_skipped`: user hoac config bo qua upload.
- `crosspost_skipped`: PostBridge tat hoac chua cau hinh.
- `crosspost_failed`: PostBridge loi sau khi YouTube upload.

Trước khi đăng video:

- Script không có stage direction như `(pause)`, `[music]`, `Narrator:` nếu TTS sẽ đọc thành tiếng.
- Title không quá dài và không sai nội dung.
- Description không chứa placeholder.
- Tags liên quan tới nội dung.
- Voice đúng ngôn ngữ.
- Caption khớp audio.
- Video không dùng ảnh sai context, ảnh lỗi mặt/tay/text, hoặc ảnh có watermark không mong muốn.
- Không publish tự động nếu chưa xem video output.

## 17. Ghi nhớ quan trọng

- `config.json` là cấu hình local, không commit.
- `.mp/` là dữ liệu runtime, không coi là source code.
- Muốn sửa logic provider, dùng `src/providers/` và `src/llm_provider.py`, không gọi API trực tiếp từ feature code.
- Muốn sửa config, dùng helper trong `src/config.py`, không đọc `config.json` trực tiếp trong business logic mới.
- Khi sửa TTS voice/model, phải giữ đồng bộ giữa config, API, UI, và `src/classes/Tts.py`.

## 18. Cap nhat Phase 2-5 trong backend

### Subtitle glossary va adapt script

API generate va translate da nhan field `glossary` theo dang:

```text
AI Agent = tac nhan AI
workflow = quy trinh
```

Khi co `script` custom, backend se normalize truoc khi dua vao TTS:

- Bo nhan cau truc nhu `Hook:`, `CTA:`, `Main points:`.
- Ap dung glossary neu co.
- Luu `original_script` va `subtitle_adaptation` vao `session.json`.

Endpoint lien quan:

```text
POST /youtube/{account_id}/translate-script
POST /youtube/{account_id}/generate
```

### Renderer track

`renderer = "moviepy"` van la mac dinh va la duong render MP4 chinh.

`renderer = "html"` hien la prototype: backend co `src/renderers/html_renderer.py` de ghi file `.composition.html` deterministic. Chua thay MoviePy, chua render MP4 that bang browser + FFmpeg.

### Content template va style preset

API generate da nhan:

```json
{
  "template": "tips",
  "style_preset": "clean"
}
```

Template hop le:

- `tips`
- `story`
- `facts`
- `tutorial`
- `pov`

Backend luu `content_plan` va `media_selection` vao `session.json` de dung lai cho UI/renderer.

### Duplicate detection

Moi session co `content_fingerprint`. Khi generate ma khong bat `force_new_session`, backend se tim session cung subject/fingerprint de reuse hoac canh bao trung noi dung.

### Scheduler publish

Co endpoint:

```text
POST /youtube/sessions/{session_id}/schedule
```

Body mau:

```json
{
  "run_at": "2026-06-06T10:00:00+07:00",
  "platforms": ["youtube", "twitter", "affiliate"]
}
```

Backend se:

- Luu queue vao `.mp/publish_queue.json`.
- Doi session stage thanh `scheduled`.
- Khong auto upload ngay. Can worker/runner doc queue de publish that.

### Test nhanh

```powershell
python -m unittest tests.test_phase_completion -v
python -m py_compile src\subtitles\glossary.py src\subtitles\adaptation.py src\renderers\html_renderer.py src\content_engine.py src\scheduler.py src\api\youtube.py src\research_engine.py
```

## 19. Frontend Production Controls

YouTube workspace da co panel `Production Controls` de dung cac option Phase 2-5 truc tiep tu UI.

Panel nay nam trong tab YouTube, ben duoi `Subtitle Language`, truoc `Publish & Metadata Options`.

Control hien co:

- `Template`: `tips`, `story`, `facts`, `tutorial`, `pov`.
- `Style Preset`: `clean`, `cinematic`, `caption_heavy`, `fast_cut`, `minimal`.
- `Renderer`: `moviepy`, `html`.
- `Glossary`: moi dong `term = translation` hoac `term: translation`.
- `Schedule At`: thoi gian xep lich theo browser local time.
- `Schedule Platforms`: `YouTube`, `Twitter/X`, `Affiliate`.

Luu y:

- `moviepy` van la renderer chinh de tao MP4.
- `html` hien chi la prototype composition, chua render MP4 that.
- `Schedule At` hien ghi queue vao backend; worker auto publish chua bat.
- Preset UI duoc luu trong browser `localStorage` key `mp_youtube_production_controls_v1`.

Test frontend:

```powershell
cd frontend
npm.cmd run lint
npm.cmd run build
```

## 20. Parallel Image Generation

YouTube pipeline tao title cover truoc, sau do tao scene images song song. So worker lay tu `threads` trong `config.json`, nhung app clamp toi da 4 de tranh provider rate-limit.

Khuyen nghi khi dung 9Router image:

- `threads: 2` cho may/line mang on dinh vua phai.
- `threads: 3` neu provider tra anh on dinh.
- Khong nen day qua 4 vi image model co the cham hon hoac bi 429/timeout.
