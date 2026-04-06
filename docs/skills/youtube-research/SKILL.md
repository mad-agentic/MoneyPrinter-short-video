---
name: youtube-research
description: >
  Skill nghiên cứu content YouTube tự động — tìm video viral theo chủ đề,
  phân tích insight, đề xuất 5 ý tưởng content hay nhất và viết kịch bản
  đầy đủ (Hook → Nội dung → CTA) cho từng ý tưởng. Dùng khi user muốn:
  nghiên cứu xu hướng YouTube, tìm ý tưởng video ngắn (Shorts/Reels/TikTok),
  phân tích đối thủ, viết script video, hoặc tự động hóa quy trình làm content.
  LUÔN dùng skill này khi user đề cập đến: "tìm video viral", "ý tưởng video",
  "nghiên cứu chủ đề", "viết kịch bản", "script YouTube", "phân tích trend".
---

# YouTube Research & Content Ideation Skill

Skill này tái tạo workflow từ video "Claude Code + NotebookLM: Nhân Viên AI Content Tự Động":
biến quá trình research content thủ công 4-5 tiếng thành pipeline tự động 5 phút.

## Quy Trình Thực Hiện

### Bước 1 — Thu Thập Thông Tin Đầu Vào

Trước khi bắt đầu, hãy xác định:
- **Chủ đề / niche** cần nghiên cứu
- **YouTube API Key** (nếu có) — dùng script `search_youtube.py` để fetch data thật
- **Nền tảng đích**: YouTube Shorts, TikTok, Facebook Reels, Instagram Reels
- **Ngôn ngữ** kịch bản: Tiếng Việt hay Tiếng Anh

Nếu user không có API Key, dùng knowledge + web search để tổng hợp thông tin về video viral trong chủ đề đó.

### Bước 2 — Tìm & Phân Tích Video Viral

**Nếu có YouTube API Key:**
Chạy script tìm kiếm:
```bash
python scripts/search_youtube.py "<chủ đề>" "<API_KEY>" --max-results 10
```
Script trả về danh sách video với: tiêu đề, view count, like count, mô tả, channel name.

**Nếu không có API Key:**
Dùng WebSearch để tìm các video viral liên quan đến chủ đề, hoặc dựa vào kiến thức để phân tích các dạng nội dung phổ biến trong niche đó.

### Bước 3 — Phân Tích Insight (Giống NotebookLM)

Với mỗi video/nguồn nội dung tìm được, phân tích:

**Yếu tố viral:**
- Hook mở đầu có gì đặc biệt? (Câu hỏi kích thích, con số, cú twist)
- Cảm xúc chủ đạo: tò mò / sợ bỏ lỡ / cảm hứng / giải trí / giá trị thực tế
- Cấu trúc nội dung: vấn đề → giải pháp, trước-sau, bí kíp số X, listicle
- Lý do audience tương tác: comment, share, save

**Gaps & cơ hội:**
- Góc độ chưa được khai thác
- Câu hỏi thường gặp chưa được trả lời
- Xu hướng mới chưa có nhiều video

### Bước 4 — Tạo 5 Ý Tưởng Content Hay Nhất

Từ phân tích trên, brainstorm và chọn 5 ý tưởng tốt nhất theo tiêu chí:

| Tiêu chí | Mô tả |
|---|---|
| Viral potential | Có hook mạnh, dễ share, đánh đúng cảm xúc |
| Tính mới | Góc nhìn độc đáo, chưa bị làm nhiều |
| Phù hợp nền tảng | Đúng format video ngắn (60-90 giây) |
| Giá trị thực tế | Người xem học được gì / được gì |
| Dễ sản xuất | Không cần quá nhiều nguồn lực |

Trình bày mỗi ý tưởng theo format:

```
### Ý tưởng #N: [Tiêu đề hấp dẫn]
- **Góc nhìn:** [Unique angle]
- **Target audience:** [Ai sẽ xem]
- **Viral trigger:** [Cảm xúc/yếu tố kích thích share]
- **Tóm tắt nội dung:** [2-3 câu]
- **Điểm mạnh:** [Tại sao ý tưởng này tiềm năng]
```

### Bước 5 — Viết Kịch Bản Đầy Đủ

Cho ý tưởng #1 (ý tưởng hay nhất), viết kịch bản hoàn chỉnh theo cấu trúc:

```
## KỊCH BẢN: [Tên ý tưởng]

### 🎣 HOOK (0-3 giây) — BẮT BUỘC gây chú ý ngay lập tức
[Câu mở đầu cực mạnh — câu hỏi gây shock, con số bất ngờ, hoặc tuyên bố ngược đời]

### 📖 NỘI DUNG CHÍNH (3-50 giây)
[Phần thân — chia thành 3-5 đoạn ngắn, mỗi đoạn 1 ý, dùng ngôn ngữ tự nhiên như nói chuyện]

Câu 1: ...
Câu 2: ...
Câu 3: ...
[...]

### 🔥 CTA — KÊU GỌI HÀNH ĐỘNG (50-60 giây)
[Kêu gọi rõ ràng: follow, comment, share, hoặc câu hỏi để tăng engagement]

---
⏱️ Thời lượng ước tính: ~XX giây
📝 Số từ: ~XXX từ
🎯 Platform: [YouTube Shorts / TikTok / Reels]
```

Nếu user yêu cầu, viết thêm kịch bản cho các ý tưởng còn lại (#2 đến #5).

### Bước 6 — Tóm Tắt & Gợi Ý Tiếp Theo

Sau khi hoàn thành, cung cấp:
- Bảng tóm tắt 5 ý tưởng với điểm đánh giá
- Gợi ý nền tảng phù hợp nhất cho từng ý tưởng
- Checklist production: cần chuẩn bị gì để quay video

## Output Format

LUÔN trình bày theo thứ tự:
1. **Tóm tắt phân tích** (2-3 câu về trend trong niche)
2. **5 Ý tưởng** (theo format ở Bước 4)
3. **Kịch bản đầy đủ** cho ý tưởng #1 (và các ý tưởng khác nếu được yêu cầu)
4. **Bảng đánh giá** 5 ý tưởng
5. **Next steps**

## Lưu Ý Quan Trọng

- Hook phải nằm trong 3 giây đầu — đây là yếu tố quyết định viewer có xem tiếp không
- Dùng ngôn ngữ tự nhiên, tránh văn phong hàn lâm
- Câu ngắn (dưới 15 từ), mỗi câu = một ý
- Tránh jargon — viết như đang nói chuyện với bạn bè
- CTA phải cụ thể: không dùng "hãy theo dõi chúng tôi" mà dùng "comment 'CÓ' nếu bạn muốn tập tiếp theo"
