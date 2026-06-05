# MoneyPrinter Skills

This folder contains source skills and generated `.skill` packages for MoneyPrinter.

## Skills

- `moneyprinter-support`: developer support for this repository. Use it when editing backend, frontend, video pipeline, config, sessions, logs, or skill packaging.
- `youtube-research`: content research and script workflow for short videos. Use it to turn a topic into five ideas, a TTS-ready script, and MoneyPrinter handoff fields.
- `last30days`: deep research workflow for current topics from the last 30 days across Reddit, Hacker News, Polymarket, YouTube, X/Twitter, TikTok, Instagram, and web sources.

## Package All Skills

From the repository root:

```powershell
python scripts/package_skills.py
```

This writes:

- `docs/skills/moneyprinter-support.skill`
- `docs/skills/youtube-research.skill`
- `docs/skills/last30days.skill`

## Package One Skill

```powershell
python scripts/package_skills.py --skill moneyprinter-support
python scripts/package_skills.py --skill youtube-research
python scripts/package_skills.py --skill last30days
```

Generated `.skill` files are zip archives stored beside each source folder. The archive paths are relative to `docs/skills`, such as `youtube-research/SKILL.md`.

## Manual Install

Install only when you want to use a generated package outside this repository. Copy the generated `.skill` archive into a Codex-compatible skills location or import it with your local skill installer.

Do not package or install runtime data from `.mp/`, local secrets, `config.json`, `.env`, browser profiles, or generated media.

## Edit Flow

1. Edit source under `docs/skills/<skill-name>/`.
2. Run `python scripts/package_skills.py --skill <skill-name>`.
3. Inspect the generated archive if packaging behavior changed.
4. Commit source and generated package together when shipping a skill update.
