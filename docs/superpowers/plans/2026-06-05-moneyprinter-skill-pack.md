# MoneyPrinter Skill Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build repo-native MoneyPrinter skills and a deterministic packager that outputs `.skill` archives.

**Architecture:** Skill source folders live under `docs/skills/`. The packager scans folders with `SKILL.md` and writes sibling zip archives with stable ordering. Documentation explains the skill purposes and packaging/install commands.

**Tech Stack:** Markdown skills, Python 3 standard library (`argparse`, `pathlib`, `zipfile`), existing repository docs.

---

## File Structure

- Create `docs/skills/moneyprinter-support/SKILL.md`: developer-facing Codex skill for this repository.
- Modify `docs/skills/youtube-research/SKILL.md`: clean content workflow skill, preserving existing script folder.
- Create `docs/skills/README.md`: local skill pack usage and packaging guide.
- Create `scripts/package_skills.py`: deterministic `.skill` archive builder.
- Generate `docs/skills/moneyprinter-support.skill`: packaged developer skill.
- Regenerate `docs/skills/youtube-research.skill`: packaged research skill.

### Task 1: Create MoneyPrinter Developer Skill

**Files:**
- Create: `docs/skills/moneyprinter-support/SKILL.md`

- [ ] **Step 1: Write skill source**

Create `docs/skills/moneyprinter-support/SKILL.md` with frontmatter:

```markdown
---
name: moneyprinter-support
description: Use when working inside the MoneyPrinter Short Video repository: understanding architecture, editing backend/frontend code, running local commands, handling sessions, config, logs, TTS/STT/video pipeline, and packaging repo skills.
argument-hint: "fix youtube generation bug, add API endpoint, package skills, debug TTS, update frontend"
allowed-tools: Bash, Read, Write, Edit, Grep
user-invocable: true
---
```

Add sections for repo map, commands, safe edit rules, backend rules, frontend rules, session/pipeline rules, config/secrets rules, playbooks, and verification checklist.

- [ ] **Step 2: Inspect content**

Run:

```bash
Get-Content -LiteralPath docs\skills\moneyprinter-support\SKILL.md -TotalCount 80
```

Expected: valid YAML frontmatter and readable Markdown.

### Task 2: Rewrite YouTube Research Skill

**Files:**
- Modify: `docs/skills/youtube-research/SKILL.md`

- [ ] **Step 1: Replace broken-encoding content**

Write clean Markdown frontmatter:

```markdown
---
name: youtube-research
description: Use when researching short-video topics for MoneyPrinter, finding viral angles, creating five content ideas, writing TTS-ready scripts, or preparing handoff fields for YouTube Shorts, TikTok, Reels, and Facebook Reels.
argument-hint: "AI tools for students, Vietnamese finance shorts, viral cooking hacks"
allowed-tools: Bash, Read, WebSearch
user-invocable: true
---
```

Add sections for intake, source strategy, viral analysis rubric, idea format, TTS-ready script rules, MoneyPrinter handoff, output format, and quality checklist.

- [ ] **Step 2: Preserve script reference**

Confirm the skill references:

```text
scripts/search_youtube.py
```

Run:

```bash
rg -n "search_youtube.py|TTS-ready|MoneyPrinter handoff" docs\skills\youtube-research\SKILL.md
```

Expected: all three patterns found.

### Task 3: Add Skill README

**Files:**
- Create: `docs/skills/README.md`

- [ ] **Step 1: Write README**

Create usage docs with:

```markdown
# MoneyPrinter Skills

## Skills

- `moneyprinter-support`: developer support for this repository.
- `youtube-research`: content research and script workflow for short videos.

## Package

```powershell
python scripts/package_skills.py
python scripts/package_skills.py --skill moneyprinter-support
```

Generated `.skill` files are zip archives stored beside each source folder.
```

Include manual install note: copy generated `.skill` archives to a Codex-compatible skills location only when desired.

- [ ] **Step 2: Inspect README**

Run:

```bash
Get-Content -LiteralPath docs\skills\README.md
```

Expected: lists both skills and packaging commands.

### Task 4: Add Packager Script

**Files:**
- Create: `scripts/package_skills.py`

- [ ] **Step 1: Write packager**

Create Python script with these functions:

```python
def should_include(path: Path) -> bool:
    excluded_names = {"__pycache__", ".DS_Store"}
    excluded_suffixes = {".pyc", ".pyo", ".tmp", ".skill"}
    return not any(part in excluded_names for part in path.parts) and path.suffix not in excluded_suffixes

def find_skill_dirs(root: Path) -> list[Path]:
    return sorted(path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())

def package_skill(skill_dir: Path, root: Path) -> Path:
    output_path = root / f"{skill_dir.name}.skill"
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(path for path in skill_dir.rglob("*") if path.is_file() and should_include(path)):
            archive.write(file_path, file_path.relative_to(root).as_posix())
    return output_path
```

Add argparse options `--root` defaulting to `docs/skills` and `--skill` for one skill.

- [ ] **Step 2: Run syntax check**

Run:

```bash
python -m py_compile scripts/package_skills.py
```

Expected: exit code 0.

### Task 5: Package And Verify Skills

**Files:**
- Generate: `docs/skills/moneyprinter-support.skill`
- Generate: `docs/skills/youtube-research.skill`

- [ ] **Step 1: Package all skills**

Run:

```bash
python scripts/package_skills.py
```

Expected output includes both `.skill` files.

- [ ] **Step 2: Package one skill**

Run:

```bash
python scripts/package_skills.py --skill moneyprinter-support
```

Expected output includes `docs\skills\moneyprinter-support.skill`.

- [ ] **Step 3: Inspect archive contents**

Run:

```bash
python -c "import zipfile; [print(p, zipfile.ZipFile(p).namelist()) for p in ['docs/skills/moneyprinter-support.skill','docs/skills/youtube-research.skill']]"
```

Expected: `moneyprinter-support/SKILL.md` and `youtube-research/SKILL.md` appear.

### Task 6: Final Review

**Files:**
- Review: all changed files

- [ ] **Step 1: Check worktree**

Run:

```bash
git status --short
```

Expected: only planned files are changed or untracked.

- [ ] **Step 2: Search for placeholders and encoding artifacts**

Run:

```bash
rg -n "TBD|TODO|FIXME|�|Ã|â" docs\skills scripts\package_skills.py
```

Expected: no placeholder or mojibake matches in new/rewritten files.

- [ ] **Step 3: Summarize**

Report files changed, verification commands, and any residual risk.
