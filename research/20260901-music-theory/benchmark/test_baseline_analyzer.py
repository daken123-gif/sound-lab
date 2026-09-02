#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from baseline_analyzer import analyze
from generate_synthetic_benchmark import generate


def contains_period(rows: list[dict], target: float, tolerance: float = 0.035) -> bool:
    return any(abs(row["period"] - target) <= tolerance for row in rows)


class BaselineAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name)
        generate(cls.output)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_s01_retains_half_and_double_tempo_periods(self) -> None:
        result = analyze(self.output / "s01.wav")
        self.assertEqual(len(result["onsets"]), 18)
        self.assertTrue(contains_period(result["period_hypotheses"], 0.5))
        self.assertTrue(contains_period(result["period_hypotheses"], 1.0))

    def test_s02_finds_cycle_period_without_using_file_origin(self) -> None:
        result = analyze(self.output / "s02.wav")
        self.assertEqual(len(result["onsets"]), 19)
        self.assertTrue(contains_period(result["period_hypotheses"], 2.0))
        two_second = min(result["period_hypotheses"], key=lambda row: abs(row["period"] - 2.0))
        self.assertIsNotNone(two_second["phase"])
        self.assertGreater(two_second["phase"], 0.2)

    def test_s03_keeps_layer_periods(self) -> None:
        result = analyze(self.output / "s03.wav")
        self.assertEqual(len(result["onsets"]), 19)
        left = result["channel_analysis"][0]["period_hypotheses"]
        right = result["channel_analysis"][1]["period_hypotheses"]
        self.assertTrue(contains_period(left, 0.75))
        self.assertTrue(contains_period(right, 1.0))

    def test_s04_reports_acceleration_and_signed_residuals(self) -> None:
        result = analyze(self.output / "s04.wav")
        self.assertEqual(len(result["onsets"]), 22)
        curve = result["low_band_tempo_curve"]
        self.assertIsNotNone(curve)
        self.assertLess(curve["period_end"], curve["period_start"])
        residuals = result["cross_band_timing_residuals_ms"]
        self.assertTrue(any(value < -3 for value in residuals))
        self.assertTrue(any(value > 3 for value in residuals))


if __name__ == "__main__":
    unittest.main()
