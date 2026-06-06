import re


def normalize_caption_text(text: str) -> str:
    """Collapse whitespace and remove structural labels from spoken captions."""
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    value = re.sub(
        r"^(Hook|CTA|Main points?|Noi dung|Kich ban|Nội dung|Kịch bản):\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )
    return value.strip()


def split_single_line_caption(text: str, max_chars: int = 42) -> list[str]:
    """Split caption text into single-line chunks for vertical short video."""
    normalized = normalize_caption_text(text)
    if not normalized:
        return []
    words = normalized.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines
