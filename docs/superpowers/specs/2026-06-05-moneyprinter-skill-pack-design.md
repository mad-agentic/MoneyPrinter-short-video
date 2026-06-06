# MoneyPrinter Skill Pack Design

Date: 2026-06-05

## Goal

Build a repo-native skill pack for MoneyPrinter that supports two kinds of agent work:

- Developer support: help Codex understand, modify, test, and run this repository safely.
- Content workflow support: help a content agent research short-video topics, generate ideas, write TTS-ready scripts, and hand work off to MoneyPrinter.

This phase does not change backend, frontend, or runtime app behavior. It creates maintainable skill source files and a packaging script so the skills can be shipped as `.skill` archives.

## Scope

Create or update these files:

- `docs/skills/moneyprinter-support/SKILL.md`
- `docs/skills/youtube-research/SKILL.md`
- `docs/skills/README.md`
- `scripts/package_skills.py`
- Generated packages:
  - `docs/skills/moneyprinter-support.skill`
  - `docs/skills/youtube-research.skill`

Keep existing `docs/skills/youtube-research/scripts/search_youtube.py` as part of the YouTube research skill.

## Architecture

The skill pack lives under `docs/skills/`:

```text
docs/skills/
  README.md
  moneyprinter-support/
    SKILL.md
  youtube-research/
    SKILL.md
    scripts/search_youtube.py
  moneyprinter-support.skill
  youtube-research.skill
scripts/
  package_skills.py
```

`moneyprinter-support` is a Codex/developer skill for this repository. It explains the project map, common commands, safe edit rules, backend API rules, frontend rules, session pipeline rules, configuration handling, and verification checklist.

`youtube-research` is a content workflow skill. It replaces the current broken-encoding instructions with clean Vietnamese/English-friendly guidance for topic intake, source strategy, viral analysis, five idea generation, TTS-ready script writing, and MoneyPrinter handoff fields.

`package_skills.py` packages each skill folder into a sibling `.skill` zip archive. It supports packaging all skills or one named skill.

## MoneyPrinter Developer Skill

The developer skill should tell agents to follow these local patterns:

- Use `src/llm_provider.py` for LLM calls.
- Use `from config import get_config` rather than reading `config.json` directly.
- Treat `.mp/` as runtime state and avoid committing generated sessions/media.
- Preserve session-based pipeline semantics in `src/api/session_manager.py` and `src/classes/YouTube.py`.
- Use `api.log_stream.add_log` for UI-visible logs.
- Respect `api.cancel_registry` for long-running work.
- Keep backend changes scoped to `src/api/` routers or core modules as appropriate.
- Keep frontend changes consistent with the existing React/Vite UI in `frontend/src/`.
- Avoid printing or committing secrets from `config.json`, browser profiles, or API keys.

It should include command references:

- `setup.bat`
- `start_hub.bat`
- `python scripts/preflight_local.py`
- `cd src && ..\venv\Scripts\python.exe -m uvicorn api.main:app --port 15001 --reload`
- `cd frontend && npm run dev -- --port 5174`
- `cd frontend && npm run build`
- `cd frontend && npm run lint`

## YouTube Research Skill

The research skill should guide a content agent through:

1. Intake: topic, platform, language, target audience, video duration, production constraints.
2. Source strategy: use `scripts/search_youtube.py` when a YouTube API key is available; otherwise use available web/search context and clearly state assumptions.
3. Viral analysis: hooks, emotion, format, audience, comments/share/save triggers, content gaps.
4. Idea generation: exactly five ideas with title, angle, audience, viral trigger, outline, production notes, and score.
5. Script generation: TTS-ready spoken text with no labels such as `Hook:`, `CTA:`, `Main points:`, markdown, or stage directions inside the spoken script.
6. MoneyPrinter handoff: subject, script, title override, description, tags, language, subtitle preference, kids setting, publish mode.

Output should be actionable and concise. Scripts should use short spoken sentences suitable for TTS and subtitles.

## Packaging Script

`scripts/package_skills.py` behavior:

- Default root: `docs/skills`.
- Find child directories containing `SKILL.md`.
- Write `<skill-name>.skill` beside the source folder.
- Use stable archive ordering.
- Preserve paths relative to `docs/skills`, for example `youtube-research/SKILL.md`.
- Exclude generated packages, caches, temporary files, and OS metadata.
- CLI options:
  - no args: package all skills
  - `--skill <name>`: package one skill
  - `--root <path>`: package from a different skills root

## README

`docs/skills/README.md` should explain:

- What each skill does.
- How to package all skills.
- How to package one skill.
- How to manually install/copy a generated `.skill` archive into a Codex-compatible skills location if desired.
- That generated `.skill` files are zip archives.

## Verification

After implementation:

- Run `python scripts/package_skills.py`.
- Confirm both generated packages exist:
  - `docs/skills/moneyprinter-support.skill`
  - `docs/skills/youtube-research.skill`
- Run `python scripts/package_skills.py --skill moneyprinter-support`.
- Inspect package contents enough to confirm each archive contains its expected `SKILL.md` path.
- No backend/frontend tests are required because this phase does not modify runtime app code.

## Out Of Scope

- No FastAPI endpoint changes.
- No React UI changes.
- No runtime app agent mode.
- No automatic installation into `~/.codex/skills`.
- No changes to project secrets or `config.json`.

## Risks And Mitigations

- Risk: Current `youtube-research.skill` is binary and may be overwritten. Mitigation: regenerate it from clean source using the new packager.
- Risk: Skill instructions may become too broad. Mitigation: keep `moneyprinter-support` tied to this repository only and keep app runtime changes out of phase 1.
- Risk: TTS scripts may include structural labels. Mitigation: make the research skill explicitly forbid labels, markdown, and stage directions inside spoken script fields.
