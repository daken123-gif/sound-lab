#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from contextual_analyzer import analyze
from generate_synthetic_benchmark import generate


class ContextualAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name)
        generate(cls.output)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_s05_preserves_signed_shape_without_groove_ranking(self) -> None:
        result = analyze(self.output / "s05.wav")["microtiming"]
        self.assertEqual(len(result["sections"]), 3)
        self.assertTrue(all(row["quality_label"] is None for row in result["sections"]))
        relation = next(row for row in result["shape_relations"] if row["sections"] == [1, 2])
        self.assertEqual(relation["hypothesis"], "scaled_timing_shape")
        self.assertGreater(relation["signed_shape_correlation"], 0.95)
        self.assertGreater(result["sections"][2]["mean_absolute_residual_ms"], 30.0)
        quantized_relation = next(
            row for row in result["shape_relations"] if row["sections"] == [0, 1]
        )
        self.assertIsNone(quantized_relation["signed_shape_correlation"])
        self.assertEqual(
            quantized_relation["hypothesis"],
            "insufficient_variation_for_shape_comparison",
        )

    def test_s06_limits_boundary_to_timbre_stream(self) -> None:
        result = analyze(self.output / "s06.wav")["feature_boundaries"]
        timbre = result["streams"]["timbre_centroid"]
        self.assertTrue(timbre["changed"])
        self.assertAlmostEqual(timbre["boundary_seconds"], 5.0, delta=0.03)
        self.assertFalse(result["streams"]["dominant_pitch"]["changed"])
        self.assertFalse(result["streams"]["peak_amplitude"]["changed"])
        self.assertFalse(result["streams"]["rhythm_interval"]["changed"])
        self.assertTrue(all(not row["global_boundary"] for row in result["boundary_hypotheses"]))

    def test_s07_detects_role_transfer_instead_of_fixed_band_role(self) -> None:
        result = analyze(self.output / "s07.wav")["role_transfer"]
        self.assertEqual([row["pulse_anchor_band"] for row in result["segments"]], ["low", "high"])
        transfer = result["transfer_hypotheses"][0]
        self.assertAlmostEqual(transfer["time_seconds"], 5.0, delta=0.03)
        self.assertEqual(transfer["hypothesis"], "pulse_anchor_role_transfer")

    def test_s08_separates_direct_end_and_decay_tail_end(self) -> None:
        result = analyze(self.output / "s08.wav")["decay_boundaries"]
        self.assertAlmostEqual(result["direct_sound"]["end_seconds"], 3.035, delta=0.03)
        self.assertGreaterEqual(result["decay_tail"]["end_seconds"], 6.5)
        self.assertLessEqual(result["decay_tail"]["end_seconds"], 7.0)
        self.assertGreater(
            result["decay_tail"]["end_seconds"],
            result["direct_sound"]["end_seconds"] + 3.0,
        )


if __name__ == "__main__":
    unittest.main()
