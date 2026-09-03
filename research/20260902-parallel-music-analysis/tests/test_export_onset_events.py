from __future__ import annotations

import importlib.util
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/export_onset_events.py"
SPEC = importlib.util.spec_from_file_location("export_onset_events", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def click_audio(times: list[float], sample_rate: int = 8000, duration: float = 3.0) -> np.ndarray:
    audio = np.zeros(int(sample_rate * duration), dtype=np.float64)
    burst = np.hanning(40) * 0.9
    for time_s in times:
        start = int(round(time_s * sample_rate))
        audio[start : start + len(burst)] += burst
    return np.clip(audio, -1.0, 1.0)


def write_pcm(path: Path, channels: np.ndarray, sample_rate: int = 8000) -> None:
    if channels.ndim == 1:
        channels = channels[:, None]
    data = (np.clip(channels, -1.0, 1.0) * 32767.0).astype("<i2").tobytes()
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channels.shape[1])
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(data)


class ExportOnsetEventsTest(unittest.TestCase):
    def test_exports_absolute_times_and_provided_grid_offsets(self) -> None:
        expected = [0.5, 1.0, 1.5, 2.13, 2.5]
        with tempfile.TemporaryDirectory() as directory:
            wav = Path(directory) / "fixture.wav"
            write_pcm(wav, click_audio(expected))
            result = MODULE.analyze_wav(wav, "fixture", bpm=120.0, beat_origin_s=0.0)

        events = result["events"]
        self.assertEqual(len(events), len(expected))
        for event, target in zip(events, expected):
            self.assertAlmostEqual(event["absolute_time_s"], target + 0.0025, delta=0.004)
        self.assertAlmostEqual(events[3]["offset_from_clock_s"], 0.1325, delta=0.004)
        self.assertEqual(events[3]["beat_index"], 4)
        self.assertEqual(result["provided_clock"]["authority"], "caller-provided")

    def test_does_not_invent_clock_without_origin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            wav = Path(directory) / "fixture.wav"
            write_pcm(wav, click_audio([0.5, 1.0, 1.5]))
            result = MODULE.analyze_wav(wav, "fixture")

        self.assertIsNone(result["provided_clock"])
        self.assertTrue(result["events"])
        self.assertTrue(all(event["offset_from_clock_s"] is None for event in result["events"]))

    def test_rejects_half_specified_clock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            wav = Path(directory) / "fixture.wav"
            write_pcm(wav, click_audio([0.5]))
            with self.assertRaisesRegex(ValueError, "provided together"):
                MODULE.analyze_wav(wav, "fixture", bpm=120.0)

    def test_stereo_antiphase_event_is_not_cancelled(self) -> None:
        mono = click_audio([0.5, 1.0, 1.5])
        stereo = np.column_stack([mono, -mono])
        with tempfile.TemporaryDirectory() as directory:
            wav = Path(directory) / "antiphase.wav"
            write_pcm(wav, stereo)
            result = MODULE.analyze_wav(wav, "antiphase")

        self.assertEqual(len(result["events"]), 3)
        self.assertEqual(result["source"]["channels"], 2)
        self.assertEqual(
            result["source"]["analysis_collapse"], "energy_preserving_rms_across_channels"
        )


if __name__ == "__main__":
    unittest.main()
