import tempfile
import unittest
from pathlib import Path


class Phase2SubtitlePipelineTests(unittest.TestCase):
    def test_glossary_parses_terms_and_formats_prompt_context(self):
        from src.subtitles.glossary import GlossaryTerm, format_glossary_context, parse_glossary

        terms = parse_glossary("AI Agent = tác nhân AI\nworkflow: quy trình")

        self.assertEqual(
            terms,
            [
                GlossaryTerm(source="AI Agent", target="tác nhân AI"),
                GlossaryTerm(source="workflow", target="quy trình"),
            ],
        )
        self.assertIn("AI Agent -> tác nhân AI", format_glossary_context(terms))

    def test_adapt_pipeline_returns_clean_tts_script_and_metadata(self):
        from src.subtitles.adaptation import adapt_script_for_subtitles

        result = adapt_script_for_subtitles(
            "Hook: AI Agent saves time.\nCTA: Follow for more.",
            target_language="vietnamese",
            glossary_text="AI Agent = tác nhân AI",
        )

        self.assertNotIn("Hook:", result.script)
        self.assertNotIn("CTA:", result.script)
        self.assertEqual(result.target_language, "vietnamese")
        self.assertEqual(result.glossary_terms[0].source, "AI Agent")


class Phase3RendererTests(unittest.TestCase):
    def test_html_renderer_writes_deterministic_composition_html(self):
        from src.renderers.base import RenderRequest
        from src.renderers.html_renderer import HtmlRenderer

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out.mp4"
            request = RenderRequest(
                session_id="s1",
                subject="Demo subject",
                image_paths=["C:/media/one.png"],
                audio_path="C:/media/audio.wav",
                subtitle_path="C:/media/sub.srt",
                output_path=str(output),
            )
            html_path = HtmlRenderer(dry_run=True).render(request)
            html = Path(html_path).read_text(encoding="utf-8")

        self.assertIn("Demo subject", html)
        self.assertIn("C:/media/one.png", html)
        self.assertIn("data-render-width=\"1080\"", html)


class Phase4ContentEngineTests(unittest.TestCase):
    def test_template_and_media_plan_are_deterministic(self):
        from src.content_engine import build_content_plan, select_media_assets

        plan = build_content_plan("AI automation", template="tips", style_preset="clean")
        assets = select_media_assets(plan, available_backgrounds=["b.mp4", "a.mp4"], available_music=["z.mp3", "m.mp3"])

        self.assertEqual(plan.template, "tips")
        self.assertEqual(plan.sections[0], "hook")
        self.assertEqual(assets.background_video, "a.mp4")
        self.assertEqual(assets.music, "m.mp3")


class Phase5SchedulerTests(unittest.TestCase):
    def test_publish_schedule_serializes_jobs(self):
        from src.scheduler import PublishJob, build_publish_queue

        queue = build_publish_queue(
            session_id="s1",
            platforms=["youtube", "twitter", "affiliate"],
            run_at="2026-06-06T10:00:00+07:00",
        )

        self.assertEqual(
            queue,
            [
                PublishJob(session_id="s1", platform="youtube", run_at="2026-06-06T10:00:00+07:00", status="scheduled"),
                PublishJob(session_id="s1", platform="twitter", run_at="2026-06-06T10:00:00+07:00", status="scheduled"),
                PublishJob(session_id="s1", platform="affiliate", run_at="2026-06-06T10:00:00+07:00", status="scheduled"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
