#!/usr/bin/env python3
"""Tests for the blind synthetic Hunter coupling listening set."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "render_hunter_coupling_stimuli.py"
FIXTURE_PATH = ROOT / "data" / "synthetic-hunter-coupling-v1.json"
SPEC = importlib.util.spec_from_file_location("render_stimuli", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HunterListeningStimuliTests(unittest.TestCase):
    def render_twice(self):
        first = tempfile.TemporaryDirectory()
        second = tempfile.TemporaryDirectory()
        first_path = Path(first.name)
        second_path = Path(second.name)
        manifest, key = MODULE.render(FIXTURE_PATH, first_path)
        MODULE.render(FIXTURE_PATH, second_path)
        return first, second, first_path, second_path, manifest, key

    def test_three_pairwise_distinct_wavs_are_rendered(self) -> None:
        first, second, first_path, _, manifest, _ = self.render_twice()
        self.addCleanup(first.cleanup)
        self.addCleanup(second.cleanup)
        hashes = {digest(first_path / item["file"]) for item in manifest["samples"]}
        self.assertEqual(len(hashes), 3)

    def test_wav_format_and_duration_are_fixed(self) -> None:
        first, second, first_path, _, manifest, _ = self.render_twice()
        self.addCleanup(first.cleanup)
        self.addCleanup(second.cleanup)
        for item in manifest["samples"]:
            with wave.open(str(first_path / item["file"]), "rb") as audio:
                self.assertEqual(audio.getnchannels(), 2)
                self.assertEqual(audio.getsampwidth(), 2)
                self.assertEqual(audio.getframerate(), 22050)
                self.assertEqual(audio.getnframes(), 93712)

    def test_render_is_byte_deterministic(self) -> None:
        first, second, first_path, second_path, manifest, _ = self.render_twice()
        self.addCleanup(first.cleanup)
        self.addCleanup(second.cleanup)
        for item in manifest["samples"]:
            self.assertEqual(
                digest(first_path / item["file"]),
                digest(second_path / item["file"]),
            )

    def test_manifest_is_blind_and_hashes_match(self) -> None:
        first, second, first_path, _, manifest, _ = self.render_twice()
        self.addCleanup(first.cleanup)
        self.addCleanup(second.cleanup)
        manifest_text = json.dumps(manifest)
        for condition in MODULE.BLIND_ORDER.values():
            self.assertNotIn(condition, manifest_text)
        for item in manifest["samples"]:
            self.assertEqual(item["sha256"], digest(first_path / item["file"]))

    def test_answer_key_is_complete_and_separate(self) -> None:
        first, second, first_path, _, _, key = self.render_twice()
        self.addCleanup(first.cleanup)
        self.addCleanup(second.cleanup)
        self.assertEqual(set(key["mapping"]), {"sample-a", "sample-b", "sample-c"})
        self.assertEqual(set(key["mapping"].values()), set(MODULE.BLIND_ORDER.values()))
        manifest_text = (first_path / "manifest.json").read_text(encoding="utf-8")
        self.assertNotIn('"mapping"', manifest_text)
        self.assertTrue((first_path / "answer-key.json").exists())


if __name__ == "__main__":
    unittest.main()
