from dataclasses import dataclass

try:
    from subtitles.formatting import normalize_caption_text
    from subtitles.glossary import GlossaryTerm, apply_glossary, parse_glossary
except ModuleNotFoundError:  # Allows `python -m unittest` imports from repo root.
    from src.subtitles.formatting import normalize_caption_text
    from src.subtitles.glossary import GlossaryTerm, apply_glossary, parse_glossary


@dataclass(frozen=True)
class AdaptedScript:
    script: str
    target_language: str
    glossary_terms: list[GlossaryTerm]
    steps: list[str]


def adapt_script_for_subtitles(
    script: str,
    target_language: str = "",
    glossary_text: str = "",
) -> AdaptedScript:
    """Deterministic translate-reflect-adapt scaffold for TTS-ready subtitles."""
    terms = parse_glossary(glossary_text)
    cleaned_lines = []
    for line in str(script or "").splitlines():
        cleaned = normalize_caption_text(line)
        if cleaned:
            cleaned_lines.append(cleaned)

    adapted = apply_glossary(" ".join(cleaned_lines), terms)
    adapted = normalize_caption_text(adapted)
    return AdaptedScript(
        script=adapted,
        target_language=(target_language or "original").strip().lower() or "original",
        glossary_terms=terms,
        steps=["normalize", "apply_glossary", "adapt_for_tts"],
    )
