#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np


LOCAL_MODULE = Path(__file__).with_name("analyze_spanish_joint_preview.py")
REPO_MODULE = Path(__file__).resolve().parents[1] / "tools" / "analyze_spanish_joint_preview.py"
MODULE_PATH = LOCAL_MODULE if LOCAL_MODULE.exists() else REPO_MODULE
SPEC = importlib.util.spec_from_file_location("analyze_spanish_joint_preview", MODULE_PATH)
analysis = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(analysis)


class SpanishJointPreviewAnalysisTests(unittest.TestCase):
    def test_lag_sign_and_resolution(self):
        first = np.zeros(600)
        second = np.zeros(600)
        first[[100, 200, 300, 400]] = 1.0
        second[[105, 205, 305, 405]] = 1.0
        lag, score = analysis.best_lag_ms(first, second, rate=44100, hop=256)
        self.assertAlmostEqual(lag, 5 * 256 / 44100 * 1000, places=3)
        self.assertGreater(score, 0.99)

    def test_tempo_candidate_recovers_known_pulse_rate(self):
        rate, hop = 44100, 256
        frames = 3000
        target_bpm = 90.0
        interval = round(60.0 / target_bpm * rate / hop)
        pulse = np.zeros(frames)
        pulse[100::interval] = 1.0
        envelopes = {name: pulse.copy() for name in analysis.BANDS}
        candidates = analysis.tempo_candidates(envelopes, rate, hop)
        self.assertLess(abs(candidates[0]["bpm"] - target_bpm), 0.5)

    def test_windowed_lags_include_local_confidence(self):
        first = np.zeros(1400)
        second = np.zeros(1400)
        first[100::120] = 1.0
        second[103::120] = 1.0
        windows = analysis.windowed_lags(first, second, rate=44100, hop=256)
        self.assertTrue(windows)
        self.assertIn("correlation", windows[0])
        self.assertIn("start_seconds", windows[0])

    def test_analysis_hashes_the_supplied_audio(self):
        rate = 44100
        duration = 2.0
        time = np.arange(round(rate * duration)) / rate
        audio = 0.2 * np.sin(2 * np.pi * 110.0 * time)
        audio += 0.2 * np.sin(2 * np.pi * 220.0 * time)
        stereo = np.column_stack([audio, audio])
        pcm = np.round(np.clip(stereo, -1, 1) * 32767).astype("<i2")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.wav"
            with wave.open(str(path), "wb") as output:
                output.setnchannels(2)
                output.setsampwidth(2)
                output.setframerate(rate)
                output.writeframes(pcm.tobytes())
            result = analysis.analyze(path)
            self.assertEqual(result["audio"]["wav_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertIn("No source separation", result["evidence_boundary"])


if __name__ == "__main__":
    unittest.main()
