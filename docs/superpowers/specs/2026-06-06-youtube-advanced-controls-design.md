# YouTube Advanced Controls Design

## Goal

Expose the Phase 2-5 backend controls in the YouTube workspace so a user can configure content template, style preset, renderer, glossary, and publish scheduling from the UI before starting generation.

## Scope

- Add one collapsible `Production Controls` panel in `frontend/src/App.tsx` inside the YouTube workspace.
- Persist control values in `localStorage` as user presets.
- Send these fields to `POST /youtube/{account_id}/generate` and re-generate calls:
  - `template`
  - `style_preset`
  - `renderer`
  - `glossary`
  - `schedule_at`
  - `schedule_platforms`
- Send `glossary` to `POST /youtube/{account_id}/translate-script` because backend translation already accepts it.

## Controls

- `template`: `tips`, `story`, `facts`, `tutorial`, `pov`.
- `style_preset`: `clean`, `cinematic`, `caption_heavy`, `fast_cut`, `minimal`.
- `renderer`: `moviepy`, `html`.
- `glossary`: free-form textarea. Supported examples: `AI Agent = tac nhan AI` and `workflow: quy trinh`.
- `schedule_at`: `datetime-local` input.
- `schedule_platforms`: checkbox set containing `youtube`, `twitter`, and `affiliate`.

## Behavior

- `moviepy` remains default renderer.
- `html` can be selected, but the UI shows a warning that it is currently a composition prototype and does not render real MP4 output.
- If `schedule_at` is set in the past, Generate and Re-Generate are blocked with a local validation warning.
- If `schedule_at` is set and no platforms are selected, the UI sends `youtube` as the default platform.
- If `schedule_at` is empty, the UI sends empty schedule fields and generation runs normally.
- Production controls persist locally under a versioned key so refreshing the browser keeps the selected preset.

## Out Of Scope

- Scheduler worker that auto-publishes queue items.
- HTML renderer that captures browser frames and produces MP4.
- Backend API changes, because the backend fields already exist.

## Testing

- Run frontend lint and build after implementation:
  - `npm.cmd run lint`
  - `npm.cmd run build`
- If backend is running, manually verify that Generate sends the new payload fields from the browser.
