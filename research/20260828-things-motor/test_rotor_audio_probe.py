import tempfile
import unittest
import wave
from pathlib import Path

from rotor_audio_probe import material_cases, pearson, probe, render


class AudioProbeTests(unittest.TestCase):
    def test_pearson_identical_and_silence(self) -> None:
        self.assertAlmostEqual(pearson([1.0, -1.0], [1.0, -1.0]), 1.0)
        self.assertEqual(pearson([0.0, 0.0], [1.0, -1.0]), 0.0)

    def test_all_modes_render_finite_length(self) -> None:
        tracks = material_cases(sample_rate=1_000, seconds=0.1)["unrelated"]
        for mode in ("equal_power", "linear", "correlation_compensated"):
            output, correlations = render(tracks, mode)
            self.assertEqual(len(output), 100)
            self.assertEqual(len(correlations), 4)

    def test_identical_material_is_flat_with_correlation_compensation(self) -> None:
        report = probe(sample_rate=4_000, seconds=1.0)
        identical = report["cases"]["identical"]
        self.assertAlmostEqual(
            identical["correlation_compensated"]["rms_relative_to_non_silent_track_db"],
            0.0,
            places=9,
        )
        self.assertGreater(
            identical["equal_power"]["rms_relative_to_non_silent_track_db"],
            2.0,
        )

    def test_wav_render_writes_twelve_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            probe(sample_rate=2_000, seconds=0.1, wav_dir=Path(directory))
            files = list(Path(directory).glob("*.wav"))
            self.assertEqual(len(files), 12)
            for path in files:
                self.assertGreater(path.stat().st_size, 44)
                with wave.open(str(path), "rb") as rendered:
                    self.assertEqual(rendered.getnchannels(), 1)
                    self.assertEqual(rendered.getframerate(), 2_000)
                    self.assertEqual(rendered.getnframes(), 200)


if __name__ == "__main__":
    unittest.main()
