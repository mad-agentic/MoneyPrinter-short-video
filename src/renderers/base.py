from dataclasses import dataclass
from typing import Protocol


@dataclass
class RenderRequest:
    session_id: str
    subject: str
    image_paths: list[str]
    audio_path: str
    subtitle_path: str
    output_path: str
    width: int = 1080
    height: int = 1920


class VideoRenderer(Protocol):
    def render(self, request: RenderRequest) -> str:
        """Render a video and return the output path."""
