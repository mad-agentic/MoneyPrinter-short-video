from dataclasses import dataclass


SHORT_TEMPLATES: dict[str, list[str]] = {
    "tips": ["hook", "tip_1", "tip_2", "tip_3", "cta"],
    "story": ["hook", "setup", "conflict", "turn", "lesson"],
    "facts": ["hook", "fact_1", "fact_2", "fact_3", "cta"],
    "tutorial": ["hook", "step_1", "step_2", "step_3", "result"],
    "pov": ["hook", "pov_setup", "moment", "twist", "cta"],
}

SOURCE_LABELS: dict[str, str] = {
    "general": "Web",
    "youtube": "YouTube",
    "reddit": "Reddit",
    "tiktok": "TikTok",
}


@dataclass(frozen=True)
class ContentPlan:
    topic: str
    template: str
    style_preset: str
    sections: list[str]


@dataclass(frozen=True)
class MediaSelection:
    background_video: str
    music: str
    style_preset: str


def build_content_plan(topic: str, template: str = "tips", style_preset: str = "clean") -> ContentPlan:
    selected_template = (template or "tips").strip().lower()
    if selected_template not in SHORT_TEMPLATES:
        selected_template = "tips"
    return ContentPlan(
        topic=str(topic or "").strip(),
        template=selected_template,
        style_preset=(style_preset or "clean").strip().lower() or "clean",
        sections=list(SHORT_TEMPLATES[selected_template]),
    )


def select_media_assets(
    plan: ContentPlan,
    available_backgrounds: list[str] | None = None,
    available_music: list[str] | None = None,
) -> MediaSelection:
    backgrounds = sorted(path for path in (available_backgrounds or []) if str(path).strip())
    music = sorted(path for path in (available_music or []) if str(path).strip())
    return MediaSelection(
        background_video=backgrounds[0] if backgrounds else "",
        music=music[0] if music else "",
        style_preset=plan.style_preset,
    )


def label_source(source: str) -> str:
    return SOURCE_LABELS.get((source or "").strip().lower(), (source or "Source").strip().title())
