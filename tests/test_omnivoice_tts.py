import sys
import types
import time
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class OmniVoiceTtsTests(unittest.TestCase):
    def test_default_omnivoice_reference_voice_specs_are_created(self):
        from omnivoice_refs import create_default_reference_voices

        fake_model = Mock()
        fake_model.generate.return_value = np.zeros(12, dtype=np.float32)

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("omnivoice_refs.sf.write") as write:
                registry = create_default_reference_voices(fake_model, Path(tmpdir))

        self.assertEqual([voice["id"] for voice in registry["voices"]], ["vi_female_ref", "vi_male_ref", "en_female_ref"])
        self.assertEqual(fake_model.generate.call_count, 3)
        self.assertEqual(write.call_count, 3)
        for voice in registry["voices"]:
            self.assertIn("ref_audio", voice)
            self.assertIn("ref_text", voice)
            self.assertIn("instruct", voice)

    def test_omnivoice_synthesizes_long_text_in_seeded_chunks(self):
        from classes.Tts import TTS

        tts = TTS.__new__(TTS)
        tts._voice = "Milo"
        tts._language = "vietnamese"
        fake_model = Mock()
        fake_model.generate.return_value = np.zeros(12, dtype=np.float32)
        tts._get_omnivoice_model = Mock(return_value=fake_model)

        text = " ".join(["Day la mot cau noi dai de tao audio on dinh."] * 18)

        with (
            patch("classes.Tts.get_omnivoice_instruct", return_value=""),
            patch("classes.Tts._seed_omnivoice_generation") as seed,
            patch("classes.Tts.info"),
            patch("classes.Tts.sf.write") as write,
        ):
            result = tts._synthesize_with_omnivoice(text, "out.wav")

        self.assertEqual(result, "out.wav")
        self.assertGreater(fake_model.generate.call_count, 1)
        self.assertEqual(seed.call_count, fake_model.generate.call_count)
        self.assertEqual([call.args[0] for call in seed.call_args_list], [424242] * fake_model.generate.call_count)
        for call in fake_model.generate.call_args_list:
            self.assertLessEqual(len(call.kwargs["text"]), 220)
            self.assertEqual(call.kwargs["instruct"], "male, low pitch")
            self.assertNotIn("audio_chunk_duration", call.kwargs)
            self.assertNotIn("audio_chunk_threshold", call.kwargs)
        write.assert_called_once()
        written_audio = write.call_args.args[1]
        self.assertEqual(len(written_audio), fake_model.generate.call_count * 12)

    def test_omnivoice_reference_voice_is_reused_for_every_chunk(self):
        from classes.Tts import TTS

        tts = TTS.__new__(TTS)
        tts._voice = "vi_female_ref"
        tts._language = "vietnamese"
        fake_model = Mock()
        fake_model.generate.return_value = np.zeros(12, dtype=np.float32)
        tts._get_omnivoice_model = Mock(return_value=fake_model)

        text = " ".join(["Day la mot cau noi dai de tao audio on dinh."] * 18)
        ref = {
            "id": "vi_female_ref",
            "ref_audio": "assets/omnivoice_refs/vi_female_ref.wav",
            "ref_text": "Day la giong mau tieng Viet on dinh.",
        }

        with (
            patch("classes.Tts.resolve_omnivoice_reference_voice", return_value=ref),
            patch("classes.Tts.get_omnivoice_instruct", return_value=""),
            patch("classes.Tts._seed_omnivoice_generation"),
            patch("classes.Tts.info"),
            patch("classes.Tts.sf.write"),
        ):
            tts._synthesize_with_omnivoice(text, "out.wav")

        self.assertGreater(fake_model.generate.call_count, 1)
        for call in fake_model.generate.call_args_list:
            self.assertEqual(call.kwargs["ref_audio"], ref["ref_audio"])
            self.assertEqual(call.kwargs["ref_text"], ref["ref_text"])
            self.assertNotIn("instruct", call.kwargs)

    def test_omnivoice_logs_heartbeat_while_chunk_is_generating(self):
        from classes.Tts import TTS

        tts = TTS.__new__(TTS)
        tts._voice = "Milo"
        tts._language = "vietnamese"

        def slow_generate(**kwargs):
            time.sleep(0.05)
            return np.zeros(12, dtype=np.float32)

        fake_model = Mock()
        fake_model.generate.side_effect = slow_generate
        tts._get_omnivoice_model = Mock(return_value=fake_model)

        with (
            patch("classes.Tts.OMNIVOICE_HEARTBEAT_INTERVAL_SECONDS", 0.01),
            patch("classes.Tts.OMNIVOICE_POSSIBLE_HANG_SECONDS", 999),
            patch("classes.Tts.get_omnivoice_instruct", return_value=""),
            patch("classes.Tts._seed_omnivoice_generation"),
            patch("classes.Tts.info") as info,
            patch("classes.Tts.sf.write"),
        ):
            tts._synthesize_with_omnivoice("Day la mot doan ngan de test heartbeat.", "out.wav")

        messages = [call.args[0] for call in info.call_args_list]
        self.assertTrue(any("OmniVoice chunk 1/1 still generating" in message for message in messages))
        self.assertTrue(any("OmniVoice chunk 1/1 done" in message for message in messages))

    def test_omnivoice_voice_presets_map_to_supported_instructs(self):
        from classes.Tts import _voice_to_omnivoice_instruct

        self.assertEqual(_voice_to_omnivoice_instruct("EN Nova"), "female, young adult, high pitch, american accent")
        self.assertEqual(_voice_to_omnivoice_instruct("EN Sage"), "male, elderly, low pitch, british accent")
        self.assertEqual(_voice_to_omnivoice_instruct("VI Hoai"), "female, young adult, moderate pitch")
        self.assertEqual(_voice_to_omnivoice_instruct("VI Minh"), "male, young adult, moderate pitch")
        self.assertEqual(_voice_to_omnivoice_instruct("VI Thoai"), "male, middle-aged, low pitch")

    def test_omnivoice_keeps_local_voice_for_vietnamese_script(self):
        def module(name, **attrs):
            mod = types.ModuleType(name)
            for key, value in attrs.items():
                setattr(mod, key, value)
            return mod

        class Dummy:
            pass

        stubs = {
            "cache": module("cache", get_accounts=lambda platform: []),
            "classes.YouTube": module("classes.YouTube", YouTube=Dummy),
            "classes.Tts": module("classes.Tts", TTS=Dummy),
            "post_bridge_integration": module("post_bridge_integration", maybe_crosspost_youtube_short=lambda *args, **kwargs: None),
            "api.session_manager": module(
                "api.session_manager",
                create_session=lambda *args, **kwargs: None,
                find_session_by_fingerprint=lambda *args, **kwargs: None,
                find_session_by_subject=lambda *args, **kwargs: None,
                get_session=lambda *args, **kwargs: None,
            ),
            "api.log_stream": module("api.log_stream", add_log=lambda *args, **kwargs: None),
            "api.cancel_registry": module(
                "api.cancel_registry",
                request_cancel=lambda *args, **kwargs: None,
                is_cancelled=lambda *args, **kwargs: False,
                clear_cancel=lambda *args, **kwargs: None,
                GenerationCancelledError=type("GenerationCancelledError", (Exception,), {}),
            ),
            "llm_provider": module("llm_provider", ensure_model_selected=lambda *args, **kwargs: "model"),
            "content_fingerprint": module("content_fingerprint", content_fingerprint=lambda *args, **kwargs: "fingerprint"),
            "content_engine": module("content_engine", build_content_plan=lambda *args, **kwargs: None, select_media_assets=lambda *args, **kwargs: []),
            "scheduler": module("scheduler", build_publish_queue=lambda *args, **kwargs: [], save_publish_queue=lambda *args, **kwargs: None),
            "subtitles.adaptation": module("subtitles.adaptation", adapt_script_for_subtitles=lambda *args, **kwargs: None),
        }

        sys.modules.pop("api.youtube", None)
        with patch.dict(sys.modules, stubs):
            from api.youtube import _resolve_tts_voice

            self.assertEqual(_resolve_tts_voice("Milo", "vietnamese", "omnivoice"), "Milo")


if __name__ == "__main__":
    unittest.main()
