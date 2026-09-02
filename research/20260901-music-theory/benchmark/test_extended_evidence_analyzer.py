#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from extended_evidence_analyzer import analyze
from generate_synthetic_benchmark import generate


class ExtendedEvidenceAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name)
        generate(cls.output)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_s09_preserves_stereo_cycle_beyond_mono_onset_period(self) -> None:
        result = analyze(self.output / "s09.wav")["spatial_periodicity"]
        self.assertEqual(result["analysis_order"], "stereo_before_mono")
        self.assertAlmostEqual(result["mono_onset_period_seconds"], 0.5, delta=0.02)
        self.assertAlmostEqual(result["spatial_cycle"]["period_seconds"], 1.0, delta=0.03)
        self.assertEqual(result["spatial_cycle"]["event_lag"], 2)
        self.assertLessEqual(result["candidate_lags"][0]["balance_similarity"], 0.05)

    def test_s10_keeps_repetition_topology_and_dynamics_transformation(self) -> None:
        result = analyze(self.output / "s10.wav")["repetition_transformation"]
        self.assertEqual(len(result["cycles"]), 4)
        self.assertEqual(
            result["hypothesis"],
            "rhythmic_repetition_with_dynamics_transformation",
        )
        self.assertLessEqual(result["onset_topology_max_error_seconds"], 0.01)
        self.assertGreater(result["onset_strength_range"], 0.05)
        self.assertLessEqual(result["dominant_frequency_range_hz"], 1.0)
        self.assertFalse(result["exact_audio_repeat"])

    def test_s11_retains_each_cycle_period_and_drift(self) -> None:
        result = analyze(self.output / "s11.wav")["cycle_drift"]
        periods = [row["period_seconds"] for row in result["cycles"]]
        self.assertEqual(len(periods), 5)
        for observed, expected in zip(periods, [1.8, 1.95, 2.1, 2.25, 2.4]):
            self.assertAlmostEqual(observed, expected, delta=0.03)
        self.assertTrue(result["time_varying"])
        self.assertGreater(result["period_trend_seconds_per_cycle"], 0.1)
        self.assertAlmostEqual(result["period_summary_median_seconds"], 2.1, delta=0.03)

    def test_s12_reports_overlap_without_naming_stems_as_truth(self) -> None:
        result = analyze(self.output / "s12.wav")["overlap_uncertainty"]
        primary = {row["frequency_hz"] for row in result["resonance_candidates"][:2]}
        self.assertEqual(primary, {62.0, 66.0})
        self.assertEqual(result["identity_status"], "unresolved_from_mixture")
        self.assertIsNone(result["source_assignment"])
        self.assertEqual(
            result["separation_status"],
            "model_hypothesis_not_observed_ground_truth",
        )
        self.assertGreater(result["energy_flux_onset_count"], 36)


if __name__ == "__main__":
    unittest.main()
