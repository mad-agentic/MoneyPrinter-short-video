from dataclasses import asdict, dataclass
import json
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


VALID_PLATFORMS = {"youtube", "twitter", "affiliate"}
SCHEDULED_STATUS = "scheduled"


@dataclass(frozen=True)
class PublishJob:
    session_id: str
    platform: str
    run_at: str
    status: str = SCHEDULED_STATUS


def build_publish_queue(session_id: str, platforms: list[str], run_at: str) -> list[PublishJob]:
    normalized = []
    for platform in platforms:
        value = str(platform or "").strip().lower()
        if value in VALID_PLATFORMS and value not in normalized:
            normalized.append(value)
    return [
        PublishJob(
            session_id=str(session_id or "").strip(),
            platform=platform,
            run_at=str(run_at or "").strip(),
        )
        for platform in normalized
    ]


def scheduler_path() -> str:
    path = os.path.join(ROOT_DIR, ".mp", "publish_queue.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def save_publish_queue(jobs: list[PublishJob], path: str | None = None) -> str:
    target = path or scheduler_path()
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as file:
        json.dump([asdict(job) for job in jobs], file, ensure_ascii=False, indent=2)
    return target
