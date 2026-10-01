#!/usr/bin/env python3

from __future__ import annotations

import math
import hashlib
import importlib.util
import struct
import tempfile
import unittest
import wave
from pathlib import Path


LOCAL_MODULE = Path(__file__).with_name("analyze_hunter_stimuli_v2.py")
REPO_MODULE = Path(__file__).resolve().parents[1] / "tools" / "analyze_hunter_stimuli_v2.py"
MODULE_PATH = LOCAL_MODULE if LOCAL_MODULE.exists() else REPO_MODULE
SPEC = importlib.util.spec_from_file_location("analyze_hunter_stimuli_v2", MODULE_PATH)
analyzer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(analyzer)


RATE = 22050
SLOTS = {
    "fixed_macro": [(0.966667, .62), (0.966667, .62), (0.966667, .62), (2.04, .62), (2.04, .62), (2.04, .62), (3., .60), (3., .60), (3., .60)],
    "hunter_coupling": [(0.90, .62), (0.96, .62), (1.04, .62), (1.98, .62), (2.02, .62), (2.12, .62), (3., .50), (3., .40), (3.04, .90)],
    "independent_voice": [(0.90, .62), (1., .62), (1., .62), (2., .62), (2., .62), (2.12, .62), (3., .70), (3., .40), (3., .70)],
}
VOICES = ["bass", "chord", "melody"] * 3
PANS = {"bass": 0.0, "chord": -0.5, "melody": 0.5}
EXPECTED = {
    "fixed_macro": "e2e32e0e5f9cf22dc98cc9c3ad7d0e98ceff0109ccce65dd779d282c0a2c5ff3",
    "hunter_coupling": "9884dc3b3fad9b95df27e90fb8f3ab8122605f392a82c44f2bd677c059325d5e",
    "independent_voice": "08907b97d35566dae0d837da7eebb5a573c4fd231f76d8779e159a8056104cf1",
}


def render(path: Path, condition: str, gain: float = 0.12) -> None:
    length = round(4.25 * RATE)
    left, right = [0.0] * length, [0.0] * length
    for onset in (1.0, 2.0, 3.0):
        start, count = round(onset * RATE), round(0.012 * RATE)
        for offset in range(count):
            position = offset / RATE
            edge = min(1.0, position / 0.003, (0.012 - position) / 0.004)
            value = math.sin(2 * math.pi * 1320 * position) * max(0.0, edge) * 0.018
            left[start + offset] += value; right[start + offset] += value
    for voice, (onset, duration) in zip(VOICES, SLOTS[condition]):
        frequency = analyzer.VOICE_FREQUENCIES[voice]
        angle = (PANS[voice] + 1.0) * math.pi / 4.0
        l_pan, r_pan = math.cos(angle), math.sin(angle)
        start, count = round(onset * RATE), round(duration * RATE)
        for offset in range(count):
            position = offset / RATE
            edge = min(1.0, position / 0.012, (duration - position) / 0.04)
            value = max(0.0, edge) * math.sin(2 * math.pi * frequency * position)
            left[start + offset] += value * l_pan; right[start + offset] += value * r_pan
    energy = sum(x*x for x in left) + sum(x*x for x in right)
    scale = gain if gain != 0.12 else (10 ** (-21 / 20)) / math.sqrt(energy / (2 * length))
    left = [x * scale for x in left]; right = [x * scale for x in right]
    start, count = round(0.25 * RATE), round(0.012 * RATE)
    for offset in range(count):
        position = offset / RATE
        edge = min(1.0, position / 0.003, (0.012 - position) / 0.004)
        value = math.sin(2 * math.pi * 880 * position) * max(0.0, edge) * 0.55
        left[start + offset] += value; right[start + offset] += value
    pcm = b"".join(struct.pack("<hh", round(max(-1, min(1, l)) * 32767), round(max(-1, min(1, r)) * 32767)) for l, r in zip(left, right))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2); output.setsampwidth(2); output.setframerate(RATE); output.writeframes(pcm)


class AudioRecoveryTests(unittest.TestCase):
    def test_recovers_all_three_conditions_from_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            for condition in SLOTS:
                path = Path(directory) / f"{condition}.wav"
                render(path, condition)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), EXPECTED[condition])
                result = analyzer.analyze(path)
                self.assertEqual(result["estimated_condition"], condition)
                for index, (expected_onset, expected_duration) in enumerate(SLOTS[condition]):
                    gesture = f"g{index // 3 + 1}"
                    voice = VOICES[index]
                    recovered = result["gestures"][gesture][voice]
                    self.assertLessEqual(abs(recovered["onset"] - expected_onset), 0.015)
                    self.assertLessEqual(abs(recovered["duration"] - expected_duration), 0.015)

    def test_classification_survives_global_gain_change(self):
        with tempfile.TemporaryDirectory() as directory:
            for gain in (0.04, 0.08, 0.20):
                for condition in SLOTS:
                    path = Path(directory) / f"{condition}-{gain}.wav"
                    render(path, condition, gain)
                    self.assertEqual(analyzer.analyze(path)["estimated_condition"], condition)


if __name__ == "__main__":
    unittest.main()
