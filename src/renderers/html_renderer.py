from html import escape
from pathlib import Path

try:
    from renderers.base import RenderRequest
except ModuleNotFoundError:  # Allows `python -m unittest` imports from repo root.
    from src.renderers.base import RenderRequest


class HtmlRenderer:
    """Prototype HTML renderer track for deterministic composition testing."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def render(self, request: RenderRequest) -> str:
        html_path = Path(request.output_path).with_suffix(".composition.html")
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(self._build_html(request), encoding="utf-8")
        if self.dry_run:
            return str(html_path)
        raise NotImplementedError("HTML MP4 rendering requires browser + FFmpeg integration")

    def _build_html(self, request: RenderRequest) -> str:
        images = "\n".join(
            f'<img class="frame-image" src="{escape(path)}" alt="">'
            for path in request.image_paths
        )
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(request.subject)}</title>
  <style>
    html, body {{ margin: 0; width: 100%; height: 100%; background: #05070b; }}
    .stage {{ width: {request.width}px; height: {request.height}px; overflow: hidden; position: relative; font-family: Arial, sans-serif; }}
    .frame-image {{ width: 100%; height: 100%; object-fit: cover; position: absolute; inset: 0; }}
    .title {{ position: absolute; left: 64px; right: 64px; bottom: 180px; color: white; font-size: 64px; font-weight: 800; line-height: 1.05; text-shadow: 0 4px 18px #000; }}
  </style>
</head>
<body>
  <main class="stage" data-render-width="{request.width}" data-render-height="{request.height}" data-session-id="{escape(request.session_id)}">
    {images}
    <div class="title">{escape(request.subject)}</div>
    <data id="audio" value="{escape(request.audio_path)}"></data>
    <data id="subtitles" value="{escape(request.subtitle_path)}"></data>
  </main>
</body>
</html>
"""
