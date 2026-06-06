import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from providers.ninerouter import NineRouterProvider


class NineRouterTtsTests(unittest.TestCase):
    def test_edge_voice_list_omits_auth_and_parses_voice_id(self):
        provider = NineRouterProvider({"base_url": "http://router", "api_key": "bad-key"})
        response = Mock(ok=True)
        response.json.return_value = {"data": [{"voice_id": "vi-VN-HoaiMyNeural"}, {"model": "vi-VN-NamMinhNeural"}]}

        with patch("providers.ninerouter.requests.get", return_value=response) as get:
            voices = provider.list_voices("edge-tts")

        self.assertEqual(voices, ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"])
        self.assertNotIn("Authorization", get.call_args.kwargs["headers"])

    def test_edge_speech_omits_auth_for_noauth_provider(self):
        provider = NineRouterProvider({
            "base_url": "http://router",
            "api_key": "bad-key",
            "tts_model": "edge-tts/vi-VN-HoaiMyNeural",
            "tts_response_format": "wav",
        })
        response = Mock(ok=True, content=b"audio")
        response.headers = {"Content-Type": "audio/wav"}

        with patch("providers.ninerouter.requests.post", return_value=response) as post:
            with patch.object(provider, "_write_media_response"):
                provider.synthesize_speech("Xin chao", "out.wav")

        self.assertNotIn("Authorization", post.call_args.kwargs["headers"])


if __name__ == "__main__":
    unittest.main()
