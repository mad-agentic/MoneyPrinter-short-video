---
name: youtube-research
description: Use when researching short-video topics for MoneyPrinter, finding viral angles, creating five content ideas, writing TTS-ready scripts, or preparing handoff fields for YouTube Shorts, TikTok, Reels, and Facebook Reels.
argument-hint: "AI tools for students, Vietnamese finance shorts, viral cooking hacks"
allowed-tools: Bash, Read, WebSearch
user-invocable: true
---

# YouTube Research For MoneyPrinter

Use this skill when the user wants short-video research, viral idea generation, script writing, or a ready handoff into MoneyPrinter.

The goal is to turn a topic into production-ready short-video inputs:

- Trend and audience insight.
- Five strong ideas.
- One complete TTS-ready script by default.
- Optional scripts for the remaining ideas when asked.
- MoneyPrinter handoff fields for video generation.

## Intake

Before research, identify these fields. Ask only for missing information that materially changes the output.

- Topic or niche.
- Target platform: YouTube Shorts, TikTok, Instagram Reels, Facebook Reels, or cross-platform.
- Script language: Vietnamese, English, or another language.
- Target audience.
- Desired duration: usually 30, 45, or 60 seconds.
- Style: educational, story, facts, tutorial, POV, reaction, product, affiliate, entertainment.
- Production constraints: faceless video, AI images, stock footage, voiceover only, on-camera, product footage.
- Any forbidden claims, sensitive topics, compliance limits, or brand voice rules.

If the user gives only a topic, continue with sensible defaults:

- Platform: YouTube Shorts.
- Language: Vietnamese if the user writes Vietnamese, otherwise English.
- Duration: 45 to 60 seconds.
- Style: practical, high-retention, voiceover-friendly.
- Production: faceless video using MoneyPrinter images, TTS, subtitles, and generated metadata.

## Source Strategy

Use the best available source path.

### With YouTube API Key

If the user provides a YouTube API key, use the bundled script:

```powershell
python docs\skills\youtube-research\scripts\search_youtube.py "<topic>" "<API_KEY>" --max-results 10
```

Analyze titles, channels, descriptions, views, likes, and recurring formats. Do not expose the API key.

### Without YouTube API Key

Use available web/search context or platform knowledge. Clearly label anything inferred from general knowledge rather than measured data.

Useful search angles:

- `site:youtube.com <topic> shorts viral`
- `site:tiktok.com <topic> viral`
- `site:reddit.com <topic> discussion`
- `<topic> trends short video ideas`

When latest/current trend accuracy matters, search the web before making claims.

## Viral Analysis Rubric

For each strong source or pattern, extract:

- Hook: first 1 to 3 seconds and why it works.
- Emotion: curiosity, fear of missing out, surprise, relief, aspiration, status, humor, controversy.
- Format: list, before/after, myth-busting, story, mistake, tutorial, challenge, ranking, reaction.
- Audience: who cares and why now.
- Engagement trigger: why viewers comment, share, save, or rewatch.
- Production pattern: visuals, pacing, voice, captions, CTA.
- Gap: unanswered question or underused angle.

Prefer concrete observations over generic advice.

## Idea Format

Generate exactly five ideas unless the user requests another count.

For each idea, output:

```markdown
### Idea #N: <short title>
- Angle: <unique angle>
- Target audience: <who watches>
- Viral trigger: <emotion or share reason>
- Format: <tips/story/facts/tutorial/trend/pov/reaction/product>
- Main points: <3 concise bullets or short phrases>
- Production notes: <visuals, pacing, assets>
- Score: <1-10> for viral potential and feasibility
```

Pick the best idea as `Recommended idea` and explain the reason in one or two sentences.

## TTS-Ready Script Rules

The spoken script must be clean text that MoneyPrinter can send to TTS.

Inside the spoken script:

- Do not include labels such as `Hook:`, `Main points:`, `CTA:`, `Scene:`, or `B-roll:`.
- Do not include markdown headings, bullets, timestamps, or stage directions.
- Do not include parenthetical camera notes.
- Use natural spoken language.
- Keep sentences short.
- Put the strongest hook in the first sentence.
- End with a specific CTA that fits the platform.

Good script shape:

```text
Most people use this tool backwards. They ask for an answer first, then wonder why the result feels generic. Try this instead. Start by giving it your goal, your audience, and one example of what good looks like. Then ask it to challenge your assumptions before writing anything. This one step makes the final output sharper because the model is no longer guessing what you care about. If you want, comment "prompt" and I will share the exact template.
```

Bad script shape:

```text
Hook: Most people use this tool backwards.
Main points:
- Give goal
- Give audience
CTA: Follow for more
```

## MoneyPrinter Handoff

After ideas and script, provide fields that map cleanly to MoneyPrinter's YouTube workflow.

```json
{
  "subject": "Short subject for the session",
  "script": "TTS-ready spoken script with no labels or markdown",
  "title_override": "SEO-friendly short title",
  "description_override": "Short description with context and CTA",
  "tags_override": "comma,separated,tags",
  "script_language": "vietnamese|english|auto",
  "publish_mode": "manual_review",
  "enable_cc": true,
  "english_cc_bottom": false,
  "is_for_kids": false
}
```

Use `manual_review` by default so the user can inspect the generated video before upload.

## Output Format

Respond in this order:

1. Research summary: 3 to 6 bullets.
2. Viral patterns: hooks, format, audience, gap.
3. Five ideas using the idea format.
4. Recommended idea.
5. Full TTS-ready script for the recommended idea.
6. MoneyPrinter handoff JSON.
7. Production checklist.

If the user asks for only scripts, skip deep analysis and still keep TTS rules.

## Quality Checklist

Before final response, verify:

- There are exactly five ideas.
- Recommended script has no labels, markdown, timestamps, or stage directions.
- First sentence works as a hook.
- Script length matches the requested duration.
- Handoff JSON has valid string fields and `publish_mode` defaults to `manual_review`.
- Tags are comma-separated.
- Any current/trend claims are sourced or clearly marked as inference.

## MoneyPrinter Notes

MoneyPrinter can generate the video from `subject` and `script`, then produce images, voiceover, subtitles, composed video, and optional upload. The generated script should be safe for TTS and subtitle segmentation.

If the user wants to create the video immediately, ask for the target YouTube account/session details or direct them to paste the handoff fields into the Web UI.
