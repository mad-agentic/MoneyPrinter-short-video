"""
research_engine.py — Web search + LLM synthesis for the Research & Idea Chat feature.

Inspired by last30days-skill (https://github.com/mvanhorn/last30days-skill)
but built natively on MoneyPrinter's existing LLM stack with zero extra API keys.
"""

import json
import re
from datetime import datetime

import status as _status

def log(level: str, message: str) -> None:
    """Proxy to status module using level string."""
    fn = getattr(_status, level.lower(), _status.info)
    fn(message, show_emoji=False)


# ── Web Search ────────────────────────────────────────────────────────────────

def search_web(query: str, max_results: int = 10) -> list[dict]:
    """
    Search the web using DuckDuckGo via the ddgs package (no API key required).

    Returns a list of dicts: [{title, url, body, published}]
    """
    try:
        # ddgs is the new name (duckduckgo_search was renamed)
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS  # fallback for older installs

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "body": r.get("body", ""),
                    "published": r.get("published", ""),
                })
        log("INFO", f"[Research] Found {len(results)} results for: {query}")
        return results
    except Exception as e:
        log("WARNING", f"[Research] Web search failed: {e}")
        return []


def search_youtube_hints(topic: str, max_results: int = 8) -> list[dict]:
    """
    Search YouTube via DuckDuckGo for trending video signals on a topic.
    Returns titles + descriptions as content hints.
    """
    query = f'site:youtube.com "{topic}" shorts OR viral OR trending 2024 OR 2025'
    return search_web(query, max_results=max_results)


def search_reddit_signals(topic: str, max_results: int = 6) -> list[dict]:
    """
    Search Reddit discussions for community engagement signals.
    """
    query = f'site:reddit.com {topic} trending discussion'
    return search_web(query, max_results=max_results)


def search_tiktok_signals(topic: str, max_results: int = 6) -> list[dict]:
    """
    Search TikTok content signals for a topic.
    """
    query = f'site:tiktok.com {topic} viral trending'
    return search_web(query, max_results=max_results)


def aggregate_search(topic: str) -> dict:
    """
    Run all search queries in parallel and aggregate results.
    Returns dict with sources as keys.
    """
    import concurrent.futures

    log("INFO", f"[Research] Searching web for: {topic}")

    sources = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        general_fut = ex.submit(search_web, f"{topic} trending viral content ideas 2025", 10)
        yt_fut = ex.submit(search_youtube_hints, topic, 6)
        reddit_fut = ex.submit(search_reddit_signals, topic, 5)
        tiktok_fut = ex.submit(search_tiktok_signals, topic, 5)

        sources["general"] = general_fut.result()
        sources["youtube"] = yt_fut.result()
        sources["reddit"] = reddit_fut.result()
        sources["tiktok"] = tiktok_fut.result()

    total = sum(len(v) for v in sources.values())
    log("SUCCESS", f"[Research] Aggregated {total} results across {len(sources)} sources")
    return sources


# ── Result Formatting ─────────────────────────────────────────────────────────

def _format_results_for_prompt(sources: dict, max_chars: int = 6000) -> str:
    """Format aggregated search results into a compact prompt-friendly string."""
    lines = []
    source_labels = {
        "general": "🌐 Web",
        "youtube": "▶️ YouTube",
        "reddit": "🟠 Reddit",
        "tiktok": "🎵 TikTok",
    }

    for source, results in sources.items():
        if not results:
            continue
        label = source_labels.get(source, source.title())
        lines.append(f"\n### {label} ({len(results)} kết quả)")
        for r in results:
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()[:200]
            url = r.get("url", "")
            if title:
                lines.append(f"- **{title}**")
                if body:
                    lines.append(f"  {body}")
                if url:
                    lines.append(f"  ({url})")

    text = "\n".join(lines)
    # Truncate to max_chars to stay within LLM context
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n...[truncated]"
    return text


# ── LLM Synthesis ─────────────────────────────────────────────────────────────

RESEARCH_SYSTEM_PROMPT = """Bạn là chuyên gia phân tích content viral cho YouTube Shorts, TikTok và Reels.
Nhiệm vụ: Dựa trên kết quả tìm kiếm thực tế, phân tích xu hướng và đề xuất góc nhìn content hiệu quả.
Trả lời ngắn gọn, súc tích, dùng bullet points. Ưu tiên insight thực tế, tránh lời khuyên chung chung."""

IDEA_SYSTEM_PROMPT = """Bạn là content strategist chuyên tạo short video viral (30-60 giây).
Nhiệm vụ: Tạo ý tưởng video có thể thực hiện ngay, với hook mạnh và cấu trúc rõ ràng.
Luôn trả về JSON hợp lệ, không có text nào bên ngoài JSON array."""


def synthesize_research(topic: str, sources: dict, conversation: list[dict]) -> str:
    """
    Use LLM to synthesize search results into actionable content insights.
    Returns a markdown string.
    """
    from llm_provider import generate_text

    results_text = _format_results_for_prompt(sources)
    convo_context = ""
    if conversation:
        recent = conversation[-4:]  # Last 4 turns for context
        convo_context = "\n\nLịch sử chat trước:\n" + "\n".join(
            f"{m['role'].upper()}: {m['content'][:300]}" for m in recent
        )

    prompt = f"""{RESEARCH_SYSTEM_PROMPT}

Topic: **{topic}**

Kết quả tìm kiếm thực tế:{results_text}{convo_context}

Dựa trên dữ liệu trên, hãy phân tích:
1. **Xu hướng hot nhất** về topic này hiện tại
2. **Góc nhìn content** nào đang được quan tâm nhiều nhất
3. **Hooks/format** nào đang viral (tips, story, fact, tutorial, POV...)
4. **Target audience** phù hợp nhất
5. **Ý tưởng sơ bộ** cho 2-3 video ngắn

Trả lời bằng markdown, ngắn gọn và actionable."""

    log("INFO", "[Research] Synthesizing research with LLM...")
    return generate_text(prompt)


def generate_video_ideas(topic: str, conversation: list[dict], context: str = "") -> list[dict]:
    """
    Generate 5 structured short video ideas as a JSON list.

    Each idea:
    {
        "id": "idea_1",
        "title": str,          # Catchy title ≤10 words
        "hook": str,           # Opening line to grab attention in 3s
        "format": str,         # tips | story | facts | tutorial | trend | pov | reaction
        "main_points": [str],  # 3 key points to cover
        "script_outline": str, # Full script for 30-60s video
        "cta": str,            # Call to action
        "target_audience": str
    }
    """
    from llm_provider import generate_text

    convo_summary = ""
    if conversation:
        # Summarize last 6 messages for context
        recent = conversation[-6:]
        convo_summary = "\n".join(
            f"{m['role'].upper()}: {m['content'][:400]}" for m in recent
        )

    prompt = f"""{IDEA_SYSTEM_PROMPT}

Topic: {topic}

{f"Context từ cuộc trò chuyện:{chr(10)}{convo_summary}" if convo_summary else ""}
{f"Research insights:{chr(10)}{context}" if context else ""}

Tạo ĐÚNG 5 ý tưởng video ngắn (30-60 giây) về topic "{topic}".

Trả về JSON array, KHÔNG có text nào bên ngoài. Format:
[
  {{
    "id": "idea_1",
    "title": "Tiêu đề hấp dẫn (tối đa 10 từ)",
    "hook": "Câu mở đầu kéo view trong 3 giây đầu",
    "format": "tips|story|facts|tutorial|trend|pov",
    "main_points": ["Điểm 1", "Điểm 2", "Điểm 3"],
    "script_outline": "Kịch bản đầy đủ cho video 30-60s: Hook → Nội dung → CTA",
    "cta": "Lời kêu gọi hành động",
    "target_audience": "Đối tượng mục tiêu"
  }},
  ...
]"""

    log("INFO", "[Research] Generating video ideas with LLM...")
    raw = generate_text(prompt)

    # Extract JSON from response (LLM may wrap it in markdown code blocks)
    ideas = _parse_json_ideas(raw)
    if not ideas:
        log("WARNING", "[Research] Failed to parse ideas JSON, returning empty list")
        return []

    # Ensure each idea has an id
    for i, idea in enumerate(ideas):
        if "id" not in idea:
            idea["id"] = f"idea_{i+1}"

    log("SUCCESS", f"[Research] Generated {len(ideas)} video ideas")
    return ideas


def _parse_json_ideas(text: str) -> list[dict]:
    """Extract and parse JSON array from LLM response."""
    # Try direct parse first
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Try to extract JSON array from markdown code block
    patterns = [
        r"```json\s*(\[[\s\S]*?\])\s*```",
        r"```\s*(\[[\s\S]*?\])\s*```",
        r"(\[[\s\S]*\])",  # Any JSON array
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                continue

    return []


# ── Chat Response Generator ───────────────────────────────────────────────────

def build_chat_messages(system_prompt: str, conversation: list[dict], new_message: str) -> list[dict]:
    """Build full messages list for LLM (system + history + new user message)."""
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation[-10:]:  # Keep last 10 turns to avoid context overflow
        role = msg.get("role", "user")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": new_message})
    return messages
