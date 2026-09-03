#!/usr/bin/env python3
"""Regression tests for the synthetic Hunter coupling contrast."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "simulate_hunter_coupling.py"
FIXTURE_PATH = ROOT / "data" / "synthetic-hunter-coupling-v1.json"
SPEC = importlib.util.spec_from_file_location("simulate_hunter_coupling", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class HunterCouplingContrastTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = MODULE.build_report()

    def test_generation_is_deterministic(self) -> None:
        self.assertEqual(self.report, MODULE.build_report())

    def test_all_conditions_keep_the_same_voice_slots(self) -> None:
        self.assertEqual(
            self.report["summary"]["event_slots"],
            {
                "independent_voice": 9,
                "fixed_macro": 9,
                "hunter_coupling": 9,
            },
        )
        self.assertEqual(
            self.report["summary"]["automatic_events_added"],
            {
                "independent_voice": 0,
                "fixed_macro": 0,
                "hunter_coupling": 0,
            },
        )

    def test_independent_condition_changes_one_voice_per_gesture(self) -> None:
        self.assertEqual(
            self.report["summary"]["affected_voice_counts"]["independent_voice"],
            [1, 1, 1],
        )

    def test_fixed_macro_changes_all_voices_identically(self) -> None:
        self.assertEqual(
            self.report["summary"]["affected_voice_counts"]["fixed_macro"],
            [3, 3, 3],
        )
        self.assertEqual(
            self.report["summary"]["distinct_target_patterns"]["fixed_macro"],
            [1, 1, 1],
        )

    def test_hunter_coupling_is_multi_voice_and_differentiated(self) -> None:
        self.assertEqual(
            self.report["summary"]["affected_voice_counts"]["hunter_coupling"],
            [3, 3, 3],
        )
        self.assertEqual(
            self.report["summary"]["distinct_target_patterns"]["hunter_coupling"],
            [3, 3, 3],
        )

    def test_chord_mute_preserves_other_active_voices_in_coupling_condition(self) -> None:
        slots = self.report["conditions"]["hunter_coupling"]["slots"]
        muted_gesture = {
            slot["voice"]: slot["active"]
            for slot in slots
            if slot["gesture_id"] == "g3"
        }
        self.assertEqual(
            muted_gesture,
            {"bass": True, "chord": False, "melody": True},
        )

    def test_saved_fixture_matches_generator(self) -> None:
        saved = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(saved, self.report)


if __name__ == "__main__":
    unittest.main()

