"""
Thread-safe cancellation registry for background generation tasks.

Usage:
    from api.cancel_registry import request_cancel, is_cancelled, clear_cancel

    # From API endpoint (any thread):
    request_cancel(session_id)

    # From generation thread (checked at stage boundaries):
    if is_cancelled(session_id):
        raise GenerationCancelledError(session_id)
"""
import threading

_lock = threading.Lock()
_cancelled: set[str] = set()


class GenerationCancelledError(Exception):
    def __init__(self, session_id: str):
        super().__init__(f"Generation cancelled for session {session_id}")
        self.session_id = session_id


def request_cancel(session_id: str) -> None:
    """Mark a session as requested for cancellation."""
    with _lock:
        _cancelled.add(session_id)


def is_cancelled(session_id: str) -> bool:
    """Check if a cancellation has been requested for this session."""
    with _lock:
        return session_id in _cancelled


def clear_cancel(session_id: str) -> None:
    """Remove cancellation flag (call after generation fully stops)."""
    with _lock:
        _cancelled.discard(session_id)
