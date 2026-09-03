from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/evaluate_onset_events.py"
SPEC = importlib.util.spec_from_file_location("evaluate_onset_events", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class EvaluateOnsetEventsTest(unittest.TestCase):
    def test_counts_one_match_per_reference_and_estimate(self) -> None:
        result = MODULE.evaluate([1.0], [0.99, 1.01], tolerance_s=0.05)
        self.assertEqual(result["true_positive"], 1)
        self.assertEqual(result["false_positive"], 1)
        self.assertEqual(result["false_negative"], 0)

    def test_counts_merged_detection_as_one_match(self) -> None:
        result = MODULE.evaluate([1.0, 1.04], [1.02], tolerance_s=0.05)
        self.assertEqual(result["true_positive"], 1)
        self.assertEqual(result["false_positive"], 0)
        self.assertEqual(result["false_negative"], 1)

    def test_perfect_match(self) -> None:
        result = MODULE.evaluate([0.5, 1.0, 1.5], [0.5, 1.0, 1.5])
        self.assertEqual(result["precision"], 1.0)
        self.assertEqual(result["recall"], 1.0)
        self.assertEqual(result["f_measure"], 1.0)

    def test_finds_maximum_matching_when_greedy_nearest_would_fail(self) -> None:
        result = MODULE.evaluate([0.0, 0.09], [-0.05, 0.04], tolerance_s=0.05)
        self.assertEqual(result["true_positive"], 2)
        self.assertEqual(result["matches"], [
            {"reference_index": 0, "estimated_index": 0},
            {"reference_index": 1, "estimated_index": 1},
        ])

    def test_rejects_negative_tolerance(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-negative"):
            MODULE.evaluate([1.0], [1.0], tolerance_s=-0.01)


if __name__ == "__main__":
    unittest.main()
