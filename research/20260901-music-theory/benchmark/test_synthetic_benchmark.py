#!/usr/bin/env python3

import json
import tempfile
import unittest
import wave
from pathlib import Path

from generate_synthetic_benchmark import CASES, SAMPLE_RATE, generate


class SyntheticBenchmarkTest(unittest.TestCase):
    def test_generation_and_manifest_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            manifest_path = generate(output)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(len(manifest["cases"]), len(CASES))
            self.assertEqual(
                [case["id"] for case in manifest["cases"]],
                [f"S{index:02d}" for index in range(1, 13)],
            )

            for case in manifest["cases"]:
                audio_path = output / case["audio"]["file"]
                self.assertTrue(audio_path.is_file())
                with wave.open(str(audio_path), "rb") as wav:
                    self.assertEqual(wav.getnchannels(), 2)
                    self.assertEqual(wav.getsampwidth(), 2)
                    self.assertEqual(wav.getframerate(), SAMPLE_RATE)
                    self.assertEqual(wav.getnframes(), case["audio"]["frames"])

    def test_ambiguity_and_polymeter_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = generate(Path(temporary))
            cases = {
                case["id"]: case
                for case in json.loads(path.read_text(encoding="utf-8"))["cases"]
            }
            self.assertEqual(
                {row["bpm"] for row in cases["S01"]["accepted_meter_hypotheses"]},
                {60, 120},
            )
            self.assertEqual(cases["S03"]["periods"]["joint"], 3.0)
            self.assertIn("micro_residual", cases["S04"]["beats"][0])
            self.assertEqual(cases["S06"]["boundaries"][0]["channel"], "timbre")
            self.assertEqual(cases["S09"]["periods"]["stereo_cycle"], 1.0)


if __name__ == "__main__":
    unittest.main()
