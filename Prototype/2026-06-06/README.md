# Prototype 2026-06-06

Thu muc nay gom cac prototype/feature moi duoc them trong ngay 2026-06-06.

## Da dua vao backend

- HTML renderer prototype: `src/renderers/html_renderer.py`
  - Tao file `.composition.html` co subtitle, media timeline, audio metadata.
  - Chua render MP4 that. Flow san xuat van dung MoviePy.
- Renderer registry: `src/renderers/registry.py`
  - Chon renderer theo key, mac dinh `moviepy`.
- Content templates: `src/content_engine.py`
  - Ho tro `tips`, `story`, `facts`, `tutorial`, `pov`.
- Subtitle adaptation/glossary: `src/subtitles/glossary.py`, `src/subtitles/adaptation.py`
  - Giu thuat ngu bang glossary, cat cau phu hop subtitle.
- Scheduler queue prototype: `src/scheduler.py`
  - Ghi lich vao `.mp/publish_queue.json`.
  - Chua co worker auto publish.

## Cach test nhanh

```powershell
python -m unittest tests.test_phase_completion -v
python -m py_compile src\subtitles\glossary.py src\subtitles\adaptation.py src\renderers\html_renderer.py src\renderers\registry.py src\content_engine.py src\scheduler.py src\api\youtube.py
```

## Trang thai

- Backend controls: done.
- Unit tests: done.
- Docs: done trong `docs/PROJECT_USAGE_VN.md` va `docs/PHASE_2_5_BACKEND_CONTROLS.md`.
- MP4 HTML renderer real render: pending.
- Scheduler worker auto publish: pending.
- Frontend controls cho cac option moi: done trong `frontend/src/App.tsx`.

## Frontend controls added

- `Production Controls` panel trong YouTube workspace.
- Luu preset vao `localStorage` key `mp_youtube_production_controls_v1`.
- Gui `template`, `style_preset`, `renderer`, `glossary`, `schedule_at`, `schedule_platforms` vao generate payload.
- Gui `glossary` vao translate-script payload.
