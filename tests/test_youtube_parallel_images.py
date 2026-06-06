import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class YouTubeParallelImageTests(unittest.TestCase):
    def test_parallel_image_generation_preserves_prompt_order_and_failures(self):
        from classes.YouTube import YouTube

        yt = YouTube.__new__(YouTube)
        yt.images = []
        yt._session = None
        prompts = ["slow", "fail", "fast"]

        def fake_generate_image(prompt):
            if prompt == "slow":
                time.sleep(0.12)
                return os.path.join(".mp", "slow.png")
            if prompt == "fail":
                time.sleep(0.02)
                return None
            time.sleep(0.01)
            return os.path.join(".mp", "fast.png")

        yt.generate_image = fake_generate_image

        started = time.perf_counter()
        with patch("classes.YouTube.info"), patch("classes.YouTube.warning"):
            ordered_paths, failures = yt._generate_images_parallel(prompts, max_workers=3)
        elapsed = time.perf_counter() - started

        self.assertLess(elapsed, 0.15)
        self.assertEqual(ordered_paths, [os.path.join(".mp", "slow.png"), os.path.join(".mp", "fast.png")])
        self.assertEqual(failures, 1)


if __name__ == "__main__":
    unittest.main()
