import unittest
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from api.main import app


class SystemFontsTest(unittest.TestCase):
    def test_system_fonts_lists_project_font_files(self):
        client = TestClient(app)

        response = client.get("/system/fonts")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("fonts", payload)
        self.assertIn("bold_font.ttf", payload["fonts"])
        self.assertTrue(
            all(font.lower().endswith((".ttf", ".otf", ".ttc")) for font in payload["fonts"])
        )


if __name__ == "__main__":
    unittest.main()
