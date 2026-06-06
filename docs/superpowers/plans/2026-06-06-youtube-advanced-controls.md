# YouTube Advanced Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add YouTube workspace controls for Phase 2-5 backend options and send them in generation payloads.

**Architecture:** Keep the implementation in `frontend/src/App.tsx` because the YouTube workspace is already implemented there. Add typed option constants, state persisted to `localStorage`, a validation helper, a reusable payload helper, and a single collapsible `Production Controls` panel.

**Tech Stack:** React, TypeScript, Vite, existing FastAPI endpoints.

---

### Task 1: Add Production Control State

**Files:**
- Modify: `frontend/src/App.tsx`

- [x] **Step 1: Add option constants near existing option constants**

```tsx
const PRODUCTION_PRESET_KEY = 'mp_youtube_production_controls_v1';
const TEMPLATE_OPTIONS = [
  { value: 'tips', label: 'Tips' },
  { value: 'story', label: 'Story' },
  { value: 'facts', label: 'Facts' },
  { value: 'tutorial', label: 'Tutorial' },
  { value: 'pov', label: 'POV' },
] as const;
const STYLE_PRESET_OPTIONS = [
  { value: 'clean', label: 'Clean' },
  { value: 'cinematic', label: 'Cinematic' },
  { value: 'caption_heavy', label: 'Caption Heavy' },
  { value: 'fast_cut', label: 'Fast Cut' },
  { value: 'minimal', label: 'Minimal' },
] as const;
const RENDERER_OPTIONS = [
  { value: 'moviepy', label: 'MoviePy' },
  { value: 'html', label: 'HTML Prototype' },
] as const;
const SCHEDULE_PLATFORM_OPTIONS = [
  { value: 'youtube', label: 'YouTube' },
  { value: 'twitter', label: 'Twitter/X' },
  { value: 'affiliate', label: 'Affiliate' },
] as const;
```

- [x] **Step 2: Add state inside `YouTubeWorkspace`**

```tsx
const [showProductionControls, setShowProductionControls] = useState(true);
const [contentTemplate, setContentTemplate] = useState('tips');
const [stylePreset, setStylePreset] = useState('clean');
const [renderer, setRenderer] = useState('moviepy');
const [glossary, setGlossary] = useState('');
const [scheduleAt, setScheduleAt] = useState('');
const [schedulePlatforms, setSchedulePlatforms] = useState<string[]>(['youtube']);
```

- [x] **Step 3: Add localStorage load/save effects**

```tsx
useEffect(() => {
  try {
    const raw = localStorage.getItem(PRODUCTION_PRESET_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw) as Partial<{
      contentTemplate: string;
      stylePreset: string;
      renderer: string;
      glossary: string;
      scheduleAt: string;
      schedulePlatforms: string[];
    }>;
    if (parsed.contentTemplate) setContentTemplate(parsed.contentTemplate);
    if (parsed.stylePreset) setStylePreset(parsed.stylePreset);
    if (parsed.renderer) setRenderer(parsed.renderer);
    if (typeof parsed.glossary === 'string') setGlossary(parsed.glossary);
    if (typeof parsed.scheduleAt === 'string') setScheduleAt(parsed.scheduleAt);
    if (Array.isArray(parsed.schedulePlatforms) && parsed.schedulePlatforms.length > 0) {
      setSchedulePlatforms(parsed.schedulePlatforms);
    }
  } catch {
    return;
  }
}, []);

useEffect(() => {
  localStorage.setItem(PRODUCTION_PRESET_KEY, JSON.stringify({
    contentTemplate,
    stylePreset,
    renderer,
    glossary,
    scheduleAt,
    schedulePlatforms,
  }));
}, [contentTemplate, stylePreset, renderer, glossary, scheduleAt, schedulePlatforms]);
```

### Task 2: Add Validation And Payload Helpers

**Files:**
- Modify: `frontend/src/App.tsx`

- [x] **Step 1: Add validation inside `generationWarnings`**

```tsx
if (scheduleAt) {
  const scheduledDate = new Date(scheduleAt);
  if (Number.isNaN(scheduledDate.getTime())) {
    warnings.push('Schedule time is invalid.');
  } else if (scheduledDate.getTime() <= Date.now()) {
    warnings.push('Schedule time must be in the future.');
  }
}
```

- [x] **Step 2: Include production state in `generationWarnings` dependency array**

```tsx
scheduleAt,
```

- [x] **Step 3: Add helper functions before `handleRegenerateFromStep`**

```tsx
const toggleSchedulePlatform = (platform: string) => {
  setSchedulePlatforms((prev) => {
    if (prev.includes(platform)) return prev.filter((item) => item !== platform);
    return [...prev, platform];
  });
};

const buildProductionPayload = () => ({
  renderer,
  template: contentTemplate,
  style_preset: stylePreset,
  glossary,
  schedule_at: scheduleAt,
  schedule_platforms: scheduleAt ? (schedulePlatforms.length > 0 ? schedulePlatforms : ['youtube']) : [],
});
```

### Task 3: Send Payload To Backend

**Files:**
- Modify: `frontend/src/App.tsx`

- [x] **Step 1: Add production fields to generate request body**

```tsx
...buildProductionPayload(),
```

- [x] **Step 2: Add production fields to re-generate request body**

```tsx
...buildProductionPayload(),
```

- [x] **Step 3: Add glossary to translate request body**

```tsx
body: JSON.stringify({
  script: customScript,
  target_language: scriptLanguage,
  resume_session_id: effectiveSessionId,
  glossary,
}),
```

### Task 4: Render Production Controls Panel

**Files:**
- Modify: `frontend/src/App.tsx`

- [x] **Step 1: Add panel after Subtitle Language and before Publish & Metadata Options**

```tsx
<div className="mt-4 space-y-3 border border-white/10 bg-slate-900/50 rounded-xl p-4">
  <button type="button" onClick={() => setShowProductionControls((v) => !v)} className="w-full flex items-center justify-between text-left">
    <p className="text-sm text-slate-200 font-semibold">Production Controls</p>
    <span className="text-xs text-cyan-300">{showProductionControls ? 'Hide' : 'Show'}</span>
  </button>
  {showProductionControls && (
    <div className="space-y-4">
      {/* controls here */}
    </div>
  )}
</div>
```

- [x] **Step 2: Add select controls for template, style, and renderer**

```tsx
<select value={contentTemplate} onChange={(e) => setContentTemplate(e.target.value)}>
  {TEMPLATE_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
</select>
```

- [x] **Step 3: Add glossary textarea**

```tsx
<textarea value={glossary} onChange={(e) => setGlossary(e.target.value)} rows={4} />
```

- [x] **Step 4: Add schedule controls**

```tsx
<input type="datetime-local" value={scheduleAt} onChange={(e) => setScheduleAt(e.target.value)} />
{SCHEDULE_PLATFORM_OPTIONS.map((platform) => (
  <label key={platform.value}>
    <input type="checkbox" checked={schedulePlatforms.includes(platform.value)} onChange={() => toggleSchedulePlatform(platform.value)} />
    {platform.label}
  </label>
))}
```

### Task 5: Verify

**Files:**
- Verify: `frontend/src/App.tsx`

- [x] **Step 1: Run lint**

```powershell
cd frontend
npm.cmd run lint
```

Expected: command exits `0`.

- [x] **Step 2: Run build**

```powershell
cd frontend
npm.cmd run build
```

Expected: command exits `0` and Vite build completes.
