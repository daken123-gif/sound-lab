#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


LOCAL_RECOVERY_TEST = Path(__file__).with_name("test_audio_recovery.py")
REPO_RECOVERY_TEST = Path(__file__).with_name("test_analyze_hunter_stimuli_v2.py")
RECOVERY_PATH = LOCAL_RECOVERY_TEST if LOCAL_RECOVERY_TEST.exists() else REPO_RECOVERY_TEST
RECOVERY_SPEC = importlib.util.spec_from_file_location("test_analyze_hunter_stimuli_v2", RECOVERY_PATH)
recovery = importlib.util.module_from_spec(RECOVERY_SPEC)
assert RECOVERY_SPEC.loader is not None
RECOVERY_SPEC.loader.exec_module(recovery)
render = recovery.render


LOCAL_MODULE = Path(__file__).with_name("stress_hunter_stimuli_v2.py")
REPO_MODULE = Path(__file__).resolve().parents[1] / "tools" / "stress_hunter_stimuli_v2.py"
MODULE_PATH = LOCAL_MODULE if LOCAL_MODULE.exists() else REPO_MODULE
SPEC = importlib.util.spec_from_file_location("stress_hunter_stimuli_v2", MODULE_PATH)
stress = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stress)


EXPECTED = {"sample-a": "fixed_macro", "sample-b": "hunter_coupling", "sample-c": "independent_voice"}


class PlaybackStressTests(unittest.TestCase):
    def test_records_all_cases_and_preserves_evidence_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            samples = {}
            for sample_id, condition in EXPECTED.items():
                path = root / f"{sample_id}.wav"
                render(path, condition)
                samples[sample_id] = path
            report = stress.run(samples)
        self.assertIn("not a measurement", report["evidence_boundary"])
        self.assertEqual(len(report["results"]), len(stress.CASES) * 3)

    def test_declared_recovery_matrix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            samples = {}
            for sample_id, condition in EXPECTED.items():
                path = root / f"{sample_id}.wav"
                render(path, condition)
                samples[sample_id] = path
            report = stress.run(samples)
        matrix = {(row["case"], row["sample_id"]): row["estimated_condition"] for row in report["results"]}
        for case in stress.CASES:
            for sample_id, expected in EXPECTED.items():
                target = None if case == "mono_highpass_400_6" else expected
                self.assertEqual(matrix[(case, sample_id)], target, f"{case} / {sample_id}")


if __name__ == "__main__":
    unittest.main()
