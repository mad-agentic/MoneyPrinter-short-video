import re

try:
    from subtitles.formatting import normalize_caption_text
except ModuleNotFoundError:
    from src.subtitles.formatting import normalize_caption_text


def format_srt_timestamp(seconds: float) -> str:
    total_millis = max(0, int(round(float(seconds or 0) * 1000)))
    hours = total_millis // 3_600_000
    minutes = (total_millis % 3_600_000) // 60_000
    secs = (total_millis % 60_000) // 1000
    millis = total_millis % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _split_long_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if current and len(candidate) > max_chars:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


def split_script_captions(text: str, max_chars: int = 84) -> list[str]:
    normalized = normalize_caption_text(text)
    if not normalized:
        return []
    chunks: list[str] = []
    for sentence in re.split(r"(?<=[.!?。！？])\s+", normalized):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) <= max_chars or len(sentence) <= int(max_chars * 1.35):
            chunks.append(sentence)
        else:
            chunks.extend(_split_long_text(sentence, max_chars=max_chars))
    return chunks


def build_script_srt(text: str, duration_seconds: float, max_chars: int = 84) -> str:
    chunks = split_script_captions(text, max_chars=max_chars)
    if not chunks:
        return ""
    duration = max(float(duration_seconds or 0), len(chunks) * 1.2)
    total_chars = max(1, sum(len(chunk) for chunk in chunks))
    cursor = 0.0
    lines: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        if index == len(chunks):
            end = duration
        else:
            share = duration * (len(chunk) / total_chars)
            end = min(duration, max(cursor + 0.8, cursor + share))
        lines.extend([
            str(index),
            f"{format_srt_timestamp(cursor)} --> {format_srt_timestamp(end)}",
            chunk,
            "",
        ])
        cursor = end
    return "\n".join(lines).strip() + "\n"
