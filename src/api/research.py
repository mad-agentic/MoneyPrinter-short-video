"""
research.py — FastAPI router for the Research & Idea Chat feature.

Endpoints:
  POST   /research/sessions              → create session
  GET    /research/sessions              → list sessions
  DELETE /research/sessions/{id}         → delete session
  POST   /research/sessions/{id}/chat    → chat (streaming SSE)
  GET    /research/sessions/{id}/history → conversation history
  GET    /research/sessions/{id}/ideas   → saved ideas
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.log_stream import add_log
from config import ROOT_DIR

router = APIRouter(prefix="/research", tags=["research"])

# ── Storage paths ──────────────────────────────────────────────────────────────

RESEARCH_DIR = os.path.join(ROOT_DIR, ".mp", "research")
os.makedirs(RESEARCH_DIR, exist_ok=True)


def _session_dir(session_id: str) -> str:
    return os.path.join(RESEARCH_DIR, session_id)


def _meta_path(session_id: str) -> str:
    return os.path.join(_session_dir(session_id), "meta.json")


def _conv_path(session_id: str) -> str:
    return os.path.join(_session_dir(session_id), "conversation.jsonl")


def _ideas_path(session_id: str) -> str:
    return os.path.join(_session_dir(session_id), "ideas.json")


# ── Session helpers ────────────────────────────────────────────────────────────

def _load_meta(session_id: str) -> dict | None:
    path = _meta_path(session_id)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_meta(meta: dict) -> None:
    session_id = meta["id"]
    os.makedirs(_session_dir(session_id), exist_ok=True)
    with open(_meta_path(session_id), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def _load_conversation(session_id: str) -> list[dict]:
    path = _conv_path(session_id)
    if not os.path.exists(path):
        return []
    messages = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return messages


def _append_message(session_id: str, role: str, content: str) -> None:
    msg = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
    }
    with open(_conv_path(session_id), "a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")


def _load_ideas(session_id: str) -> list[dict]:
    path = _ideas_path(session_id)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_ideas(session_id: str, ideas: list[dict]) -> None:
    with open(_ideas_path(session_id), "w", encoding="utf-8") as f:
        json.dump(ideas, f, ensure_ascii=False, indent=2)


def _list_sessions() -> list[dict]:
    sessions = []
    if not os.path.exists(RESEARCH_DIR):
        return sessions
    for entry in os.listdir(RESEARCH_DIR):
        meta_path = os.path.join(RESEARCH_DIR, entry, "meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, encoding="utf-8") as f:
                    sessions.append(json.load(f))
            except Exception:
                pass
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions


# ── Request models ─────────────────────────────────────────────────────────────

class CreateSessionBody(BaseModel):
    topic: str = ""


class ChatBody(BaseModel):
    message: str
    mode: str = "chat"  # "chat" | "research" | "ideas"


# ── SSE helpers ────────────────────────────────────────────────────────────────

def _sse(event_type: str, data: dict) -> str:
    return f"data: {json.dumps({'type': event_type, **data}, ensure_ascii=False)}\n\n"


async def _stream_generator(
    session_id: str,
    message: str,
    mode: str,
    request: Request,
) -> AsyncGenerator[str, None]:
    """
    Core streaming generator for chat responses.

    LLM calls run in asyncio.to_thread() to avoid blocking the event loop
    (critical on Windows with WindowsSelectorEventLoopPolicy).

    Modes:
      chat     → simple LLM reply
      research → web search first, then LLM synthesis
      ideas    → generate 5 structured video ideas
    """
    from llm_provider import generate_text_with_messages
    from research_engine import (
        aggregate_search,
        generate_video_ideas,
        build_chat_messages,
        _format_results_for_prompt,
        RESEARCH_SYSTEM_PROMPT,
    )

    async def _llm_call(msgs: list[dict]) -> str:
        """
        Run LLM in a thread pool and return the result.
        Uses asyncio.to_thread so it never blocks the event loop.
        """
        return await asyncio.to_thread(generate_text_with_messages, msgs)

    async def _llm_call_with_heartbeats(msgs: list[dict]):
        """
        Async generator that:
          1. Kicks off LLM call in a thread via a queue
          2. Yields SSE heartbeat comments every 2s while LLM is thinking
          3. Yields _sse("llm_result", ...) once complete

        SSE heartbeat (': ping\\n\\n') is an SSE comment — browsers ignore it but
        it resets the connection idle timer, preventing dropped connections on long LLMs.
        """
        loop = asyncio.get_event_loop()
        q: asyncio.Queue = asyncio.Queue()

        def _worker():
            try:
                text = generate_text_with_messages(msgs)
                loop.call_soon_threadsafe(q.put_nowait, ("ok", text))
            except Exception as exc:
                loop.call_soon_threadsafe(q.put_nowait, ("err", exc))

        loop.run_in_executor(None, _worker)

        while True:
            try:
                status, value = await asyncio.wait_for(q.get(), timeout=2.0)
                if status == "err":
                    raise value
                yield _sse("llm_result", {"text": value})
                return
            except asyncio.TimeoutError:
                if await request.is_disconnected():
                    return
                yield ": ping\n\n"  # SSE comment heartbeat — keeps connection alive

    async def _stream_text(text: str, chunk_size: int = 40):
        """Yield SSE chunk events for text, releasing event loop between each chunk."""
        nonlocal full_response
        for i in range(0, len(text), chunk_size):
            if await request.is_disconnected():
                return
            chunk = text[i:i + chunk_size]
            full_response += chunk
            yield _sse("chunk", {"content": chunk})
            await asyncio.sleep(0)

    full_response = ""

    try:
        # Validate session
        meta = _load_meta(session_id)
        if meta is None:
            yield _sse("error", {"message": "Session not found"})
            return

        # Save user message
        _append_message(session_id, "user", message)
        conversation = _load_conversation(session_id)

        # Update session topic if not set
        if not meta.get("topic") and message:
            meta["topic"] = message[:100]
        meta["updated_at"] = datetime.utcnow().isoformat()
        _save_meta(meta)

        topic = meta.get("topic", message)

        # ── Mode: research ───────────────────────────────────────────────────
        if mode == "research":
            yield _sse("status", {"message": f"Đang tìm kiếm thông tin về \"{topic}\"..."})

            # Web search in thread pool
            sources = await asyncio.to_thread(aggregate_search, topic)
            total = sum(len(v) for v in sources.values())
            yield _sse("status", {"message": f"Tìm thấy {total} kết quả. Đang phân tích bằng AI..."})

            results_text = _format_results_for_prompt(sources)
            synthesis_prompt = f"""Topic: **{topic}**

Kết quả tìm kiếm thực tế:
{results_text}

Yêu cầu của người dùng: {message}

Dựa trên dữ liệu trên, hãy phân tích:
1. **Xu hướng hot nhất** về topic này
2. **Góc nhìn content** được quan tâm nhiều
3. **Hooks/format** đang viral
4. **Gợi ý sơ bộ** 2-3 ý tưởng video ngắn

Trả lời ngắn gọn bằng markdown, tập trung vào insight thực tế."""

            msgs = build_chat_messages(RESEARCH_SYSTEM_PROMPT, conversation[:-1], synthesis_prompt)

            # LLM call with heartbeats to keep SSE connection alive during generation
            add_log("info", "[Research] Calling LLM for synthesis (mode=research)...")
            response_text = None
            async for event in _llm_call_with_heartbeats(msgs):
                if event.startswith(": ping"):
                    yield event  # Forward heartbeat to browser
                else:
                    data = json.loads(event[6:])  # Strip "data: "
                    response_text = data.get("text", "")

            if not response_text:
                yield _sse("error", {"message": "LLM không trả về kết quả. Kiểm tra lại LLM backend."})
                return

            async for sse_event in _stream_text(response_text):
                yield sse_event

        # ── Mode: ideas ──────────────────────────────────────────────────────
        elif mode == "ideas":
            yield _sse("status", {"message": "Đang tạo ý tưởng video..."})

            context = "\n".join(
                m["content"] for m in conversation[-8:] if m["role"] == "assistant"
            )

            # generate_video_ideas calls generate_text internally — wrap with heartbeats
            # Build the idea prompt manually to use heartbeat approach
            from research_engine import IDEA_SYSTEM_PROMPT, _parse_json_ideas
            from llm_provider import generate_text_with_messages

            convo_summary = "\n".join(
                f"{m['role'].upper()}: {m['content'][:400]}"
                for m in conversation[-6:][:-1]  # exclude last user msg
                if m.get("role") in ("user", "assistant")
            )
            idea_prompt = f"""Topic: {topic}

{"Context từ cuộc trò chuyện:" + chr(10) + convo_summary if convo_summary else ""}
{"Research insights:" + chr(10) + context if context else ""}

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
  }}
]"""
            idea_msgs = [
                {"role": "system", "content": IDEA_SYSTEM_PROMPT},
                {"role": "user", "content": idea_prompt},
            ]

            add_log("info", "[Research] Calling LLM for ideas generation...")
            raw_ideas = None
            async for event in _llm_call_with_heartbeats(idea_msgs):
                if event.startswith(": ping"):
                    yield event
                else:
                    data = json.loads(event[6:])
                    raw_ideas = data.get("text", "")

            ideas = _parse_json_ideas(raw_ideas) if raw_ideas else []

            if ideas:
                for i, idea in enumerate(ideas):
                    if "id" not in idea:
                        idea["id"] = f"idea_{i + 1}"
                _save_ideas(session_id, ideas)
                summary = f"Đã tạo **{len(ideas)} ý tưởng video** cho topic \"{topic}\":\n\n"
                for idx, idea in enumerate(ideas, 1):
                    summary += f"**{idx}. {idea.get('title', '')}**\n"
                    summary += f"- Hook: {idea.get('hook', '')}\n"
                    summary += f"- Format: {idea.get('format', '')}\n\n"

                async for sse_event in _stream_text(summary, chunk_size=30):
                    yield sse_event

                _append_message(session_id, "assistant", summary)
                yield _sse("done", {"ideas": ideas})
            else:
                error_msg = "Không thể tạo ý tưởng. Hãy thử chat thêm về topic trước."
                yield _sse("chunk", {"content": error_msg})
                _append_message(session_id, "assistant", error_msg)
                yield _sse("done", {"ideas": []})
            return

        # ── Mode: chat (default) ─────────────────────────────────────────────
        else:
            msgs = build_chat_messages(RESEARCH_SYSTEM_PROMPT, conversation[:-1], message)

            add_log("info", "[Research] Calling LLM (mode=chat)...")
            response_text = None
            async for event in _llm_call_with_heartbeats(msgs):
                if event.startswith(": ping"):
                    yield event
                else:
                    data = json.loads(event[6:])
                    response_text = data.get("text", "")

            if not response_text:
                yield _sse("error", {"message": "LLM không trả về kết quả."})
                return

            async for sse_event in _stream_text(response_text):
                yield sse_event

        # Save assistant message
        if full_response:
            _append_message(session_id, "assistant", full_response)

        yield _sse("done", {"ideas": []})

    except RuntimeError as e:
        add_log("error", f"[Research] LLM error: {e}")
        yield _sse("error", {"message": str(e)})
    except Exception as e:
        add_log("error", f"[Research] Unexpected error: {e}")
        yield _sse("error", {"message": f"Lỗi: {e}"})


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/sessions")
def create_session(body: CreateSessionBody):
    """Create a new research session."""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    meta = {
        "id": session_id,
        "topic": body.topic.strip(),
        "created_at": now,
        "updated_at": now,
    }
    _save_meta(meta)
    add_log("info", f"[Research] Created session: {session_id[:8]}… topic={body.topic or '(empty)'}")
    return meta


@router.get("/sessions")
def list_sessions():
    """List all research sessions."""
    return _list_sessions()


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a research session and all its data."""
    import shutil
    session_path = _session_dir(session_id)
    if not os.path.exists(session_path):
        raise HTTPException(status_code=404, detail="Session not found")
    shutil.rmtree(session_path)
    add_log("info", f"[Research] Deleted session: {session_id[:8]}…")
    return {"ok": True}


@router.post("/sessions/{session_id}/chat")
async def chat(session_id: str, body: ChatBody, request: Request):
    """
    Send a chat message and get a streaming response.

    Streams SSE events:
      data: {"type": "status", "message": "..."}   ← progress update
      data: {"type": "chunk", "content": "..."}    ← LLM text token
      data: {"type": "done", "ideas": [...]}        ← stream complete
      data: {"type": "error", "message": "..."}    ← error
    """
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    meta = _load_meta(session_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="Session not found")

    add_log("info", f"[Research] Chat [{body.mode}] session={session_id[:8]}…")

    return StreamingResponse(
        _stream_generator(session_id, body.message, body.mode, request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/sessions/{session_id}/history")
def get_history(session_id: str):
    """Get full conversation history for a session."""
    if _load_meta(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return _load_conversation(session_id)


@router.get("/sessions/{session_id}/ideas")
def get_ideas(session_id: str):
    """Get saved ideas for a session."""
    if _load_meta(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return _load_ideas(session_id)
