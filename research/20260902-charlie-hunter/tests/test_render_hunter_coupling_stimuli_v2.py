#!/usr/bin/env python3
"""Tests for the energy-matched synthetic Hunter-coupling listening set."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "render_hunter_coupling_stimuli_v2.py"
FIXTURE_PATH = ROOT / "data" / "synthetic-hunter-coupling-v2.json"
SPEC = importlib.util.spec_from_file_location("render_stimuli_v2", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HunterListeningStimuliV2Tests(unittest.TestCase):
    def render_twice(self):
        first = tempfile.TemporaryDirectory()
        second = tempfile.TemporaryDirectory()
        first_path = Path(first.name)
        second_path = Path(second.name)
        manifest, key = MODULE.render(FIXTURE_PATH, first_path)
        MODULE.render(FIXTURE_PATH, second_path)
        return first, second, first_path, second_path, manifest, key

    def test_format_hashes_and_determinism(self) -> None:
        first, second, first_path, second_path, manifest, _ = self.render_twice()
        self.addCleanup(first.cleanup)
        self.addCleanup(second.cleanup)
        hashes = set()
        for item in manifest["samples"]:
            path = first_path / item["file"]
            hashes.add(digest(path))
            self.assertEqual(item["sha256"], digest(path))
            self.assertEqual(digest(path), digest(second_path / item["file"]))
            with wave.open(str(path), "rb") as audio:
                self.assertEqual((audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getnframes()), (2, 2, 22050, 93712))
        self.assertEqual(len(hashes), 3)

    def test_manifest_is_blind_and_key_is_separate(self) -> None:
        first, second, first_path, _, manifest, key = self.render_twice()
        self.addCleanup(first.cleanup)
        self.addCleanup(second.cleanup)
        manifest_text = json.dumps(manifest)
        for condition in MODULE.BLIND_ORDER.values():
            self.assertNotIn(condition, manifest_text)
        self.assertEqual(set(key["mapping"].values()), set(MODULE.BLIND_ORDER.values()))
        self.assertNotIn('"mapping"', (first_path / "manifest.json").read_text(encoding="utf-8"))

    def test_note_count_and_duration_budget_are_equal(self) -> None:
        first, second, _, _, manifest, _ = self.render_twice()
        self.addCleanup(first.cleanup)
        self.addCleanup(second.cleanup)
        self.assertEqual({item["active_note_count"] for item in manifest["samples"]}, {9})
        budgets = [item["duration_sum_seconds"] for item in manifest["samples"]]
        self.assertTrue(all(value == budgets[0] for value in budgets[1:]))

    def test_global_rms_peak_and_interval_energy_are_matched(self) -> None:
        first, second, _, _, manifest, _ = self.render_twice()
        self.addCleanup(first.cleanup)
        self.addCleanup(second.cleanup)
        global_rms = [item["global_rms_dbfs"] for item in manifest["samples"]]
        peaks = [item["peak"] for item in manifest["samples"]]
        self.assertLessEqual(max(global_rms) - min(global_rms), 0.01)
        self.assertLessEqual(max(peaks) - min(peaks), 0.0001)
        for gesture in MODULE.WINDOWS:
            values = [item["interval_rms_dbfs"][gesture] for item in manifest["samples"]]
            self.assertLessEqual(max(values) - min(values), 0.25)

    def test_no_condition_uses_all_voice_mute_shortcut(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        for condition in fixture["conditions"].values():
            self.assertTrue(all(slot["active"] for slot in condition["slots"]))


if __name__ == "__main__":
    unittest.main()
