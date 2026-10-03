#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).with_name("analyze_spanish_joint_activity.py")
SPEC = importlib.util.spec_from_file_location("analyze_spanish_joint_activity", MODULE_PATH)
activity = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(activity)


class SpanishJointActivityTests(unittest.TestCase):
    def test_runs_are_end_exclusive(self):
        self.assertEqual(
            activity.runs(np.array([False, False, True, True, False])),
            [(False, 0, 2), (True, 2, 4), (False, 4, 5)],
        )

    def test_cleanup_fills_short_hole_and_rejects_short_spike(self):
        rate, hop = 100, 1
        mask = np.r_[np.ones(10), np.zeros(3), np.ones(10), np.zeros(10), np.ones(2), np.zeros(10)]
        cleaned = activity.clean_activity(mask, rate, hop)
        self.assertTrue(cleaned[:23].all())
        self.assertFalse(cleaned[23:].any())

    def test_pair_state_shares_and_transition_directions(self):
        low = np.array([1, 1, 0, 0, 1], dtype=bool)
        low_mid = np.array([0, 1, 1, 0, 0], dtype=bool)
        summary = activity.state_summary(activity.pair_states(low, low_mid))
        self.assertEqual(summary["frame_shares"], {
            "neither": 0.2, "low_only": 0.4, "low_mid_only": 0.2, "both": 0.2
        })
        self.assertEqual(summary["compressed_transition_counts"]["low_only__to__both"], 1)
        self.assertEqual(summary["compressed_transition_counts"]["both__to__low_mid_only"], 1)

    def test_analysis_keeps_hash_and_evidence_boundary(self):
        rate = 44100
        time = np.arange(rate * 3) / rate
        audio = np.where(time < 1.4, 0.3 * np.sin(2 * np.pi * 110 * time), 0.0)
        audio += np.where(time >= 1.6, 0.3 * np.sin(2 * np.pi * 330 * time), 0.0)
        pcm = np.round(np.column_stack([audio, audio]) * 32767).astype("<i2")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.wav"
            with wave.open(str(path), "wb") as output:
                output.setnchannels(2)
                output.setsampwidth(2)
                output.setframerate(rate)
                output.writeframes(pcm.tobytes())
            result = activity.analyze(path)
            self.assertEqual(result["audio"]["wav_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertIn("or attribution", result["evidence_boundary"])
            self.assertIn("activity_episodes", result["bands"]["low_45_180_hz"])
            self.assertEqual(
                [item["threshold_db"] for item in result["threshold_sensitivity"]],
                [-9.0, -12.0, -15.0],
            )


if __name__ == "__main__":
    unittest.main()
