import tempfile
import unittest
from pathlib import Path
import sys

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from analyze_preview_periodicity import analyse


class PeriodicityBaselineTest(unittest.TestCase):
    def test_recovers_click_track_periodicity(self) -> None:
        sample_rate = 22050
        bpm = 96.0
        duration = 30.0
        audio = np.zeros(int(sample_rate * duration), dtype=np.float32)
        step = sample_rate * 60.0 / bpm
        for beat in np.arange(0.0, len(audio), step):
            start = int(round(beat))
            length = min(256, len(audio) - start)
            if length > 0:
                audio[start : start + length] += np.hanning(length).astype(np.float32)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "clicks.wav"
            wavfile.write(path, sample_rate, audio)
            result = analyse(path)

        estimated = result["candidates"][0]["bpm"]
        self.assertLess(abs(estimated - bpm), 0.5)
        self.assertEqual(result["scope"], "coarse periodicity only; not beat tracking or microtiming")


if __name__ == "__main__":
    unittest.main()
