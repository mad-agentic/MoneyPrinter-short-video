import hashlib
import re


def normalize_content_key(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip().lower())
    return text


def content_fingerprint(subject: str, script: str = "") -> str:
    payload = f"{normalize_content_key(subject)}\n{normalize_content_key(script)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
