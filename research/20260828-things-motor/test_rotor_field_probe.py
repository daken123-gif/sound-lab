import tempfile
import subprocess
import unittest
import wave
from pathlib import Path

from rotor_audio_probe import sine, write_wav
from rotor_field_probe import decode_mono, field_probe


class FieldRecordingProbeTests(unittest.TestCase):
    def _fixtures(self, directory: Path, sample_rate: int = 4_000) -> list[Path]:
        paths: list[Path] = []
        for index, frequency in enumerate((173.0, 257.0, 389.0, 541.0), start=1):
            path = directory / f"track-{index}.wav"
            write_wav(path, sine(frequency, sample_rate, sample_rate), sample_rate)
            paths.append(path)
        return paths

    def test_decode_mono_wav(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = self._fixtures(Path(directory))
            samples = decode_mono(paths[0], 4_000)
            self.assertEqual(len(samples), 4_000)
            self.assertGreater(max(samples), 0.24)

    def test_decode_aac_m4a_container(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self._fixtures(root)[0]
            compressed = root / "voice-memo.m4a"
            subprocess.run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-nostdin",
                    "-i",
                    str(source),
                    "-c:a",
                    "aac",
                    str(compressed),
                ],
                check=True,
            )
            samples = decode_mono(compressed, 4_000)
            self.assertGreaterEqual(len(samples), 4_000)
            self.assertGreater(max(samples), 0.20)

    def test_probe_requires_four_recordings(self) -> None:
        with self.assertRaises(ValueError):
            field_probe([], sample_rate=4_000)

    def test_probe_reports_decode_and_switch_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = field_probe(
                self._fixtures(root),
                sample_rate=4_000,
                switch_seconds=0.2,
                ramp_ms=5.0,
            )
            self.assertEqual(report["decoder"]["channel_policy"], "downmix to mono")
            self.assertEqual(len(report["inputs"]), 4)
            self.assertEqual(report["render"]["ramp_frames"], 20)
            self.assertLess(
                report["ramped"]["coefficient_step_at_switch"],
                report["immediate"]["coefficient_step_at_switch"] / 10,
            )

    def test_probe_trims_to_shortest_and_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = self._fixtures(root)
            write_wav(paths[-1], sine(541.0, 3_000, 4_000), 4_000)
            immediate = root / "immediate.wav"
            ramped = root / "ramped.wav"
            report = field_probe(
                paths,
                sample_rate=4_000,
                switch_seconds=0.2,
                output_immediate=immediate,
                output_ramped=ramped,
            )
            self.assertTrue(all(item["trimmed_frames"] == 3_000 for item in report["inputs"]))
            for path in (immediate, ramped):
                with wave.open(str(path), "rb") as rendered:
                    self.assertEqual(rendered.getnframes(), 3_000)


if __name__ == "__main__":
    unittest.main()
