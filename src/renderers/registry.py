try:
    from renderers.html_renderer import HtmlRenderer
except ModuleNotFoundError:  # Allows `python -m unittest` imports from repo root.
    from src.renderers.html_renderer import HtmlRenderer


def get_renderer(name: str):
    renderer = (name or "moviepy").strip().lower()
    if renderer in {"html", "html_renderer"}:
        return HtmlRenderer(dry_run=True)
    if renderer in {"moviepy", "moviepy_renderer"}:
        return None
    raise ValueError(f"Unknown renderer: {name}")
