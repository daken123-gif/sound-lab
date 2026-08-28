#!/usr/bin/env python3

import math
import unittest

from rotor_layout import (
    coefficient_ramp,
    layout_coefficients,
    sector_owners,
    transition_metrics,
)


class SectorOwnerTests(unittest.TestCase):
    def test_hold_inherits_preceding_active_track_cyclically(self) -> None:
        self.assertEqual(sector_owners([True, False, True, False], "hold"), [0, 0, 2, 2])
        self.assertEqual(sector_owners([False, False, True, False], "hold"), [2, 2, 2, 2])

    def test_hole_preserves_empty_sectors(self) -> None:
        self.assertEqual(sector_owners([True, False, True, False], "hole"), [0, None, 2, None])


class LayoutCoefficientTests(unittest.TestCase):
    def test_no_active_tracks_is_silent(self) -> None:
        for mode in ("skip", "hold", "hole"):
            self.assertEqual(layout_coefficients(0.3, [False] * 4, mode), [0.0] * 4)

    def test_one_active_track_is_unity_at_every_phase(self) -> None:
        for mode in ("skip", "hold", "hole"):
            for phase in (0.0, 0.13, 0.5, 0.999):
                self.assertEqual(
                    layout_coefficients(phase, [False, True, False, False], mode),
                    [0.0, 1.0, 0.0, 0.0],
                )

    def test_hold_dwell_never_sums_duplicate_equal_power_gains(self) -> None:
        active = [True, False, True, False]
        for index in range(1024):
            coefficients = layout_coefficients(index / 1024, active, "hold")
            self.assertLessEqual(max(coefficients), 1.0)
            self.assertLessEqual(sum(coefficients), math.sqrt(2.0) + 1e-12)
        self.assertEqual(layout_coefficients(0.125, active, "hold"), [1.0, 0.0, 0.0, 0.0])

    def test_hole_fades_to_silence_at_empty_sector_midpoint(self) -> None:
        coefficients = layout_coefficients(0.375, [True, False, True, False], "hole")
        self.assertAlmostEqual(sum(coefficients), math.sqrt(0.5))
        self.assertEqual(coefficients[0], 0.0)
        self.assertEqual(coefficients[1], 0.0)

    def test_skip_redistributes_only_enabled_tracks(self) -> None:
        coefficients = layout_coefficients(0.5, [True, False, True, False], "skip")
        self.assertEqual(coefficients, [0.0, 0.0, 1.0, 0.0])

    def test_fixed_layouts_do_not_remap_an_unaffected_arc(self) -> None:
        before = [True, True, True, True]
        after = [True, True, True, False]
        for mode in ("hold", "hole"):
            self.assertEqual(
                layout_coefficients(0.1, before, mode),
                layout_coefficients(0.1, after, mode),
            )
        self.assertNotEqual(
            layout_coefficients(0.1, before, "skip"),
            layout_coefficients(0.1, after, "skip"),
        )


class TransitionTests(unittest.TestCase):
    def test_ramp_reaches_target_without_repeating_start(self) -> None:
        ramp = coefficient_ramp([1.0, 0.0], [0.0, 1.0], 4)
        self.assertEqual(ramp[0], [0.75, 0.25])
        self.assertEqual(ramp[-1], [0.0, 1.0])

    def test_ramp_bounds_per_sample_jump(self) -> None:
        metrics = transition_metrics(
            0.19,
            [True, True, True, True],
            [True, False, True, False],
            "skip",
            240,
        )
        self.assertLessEqual(
            metrics["ramped_max_per_sample_coefficient_jump"],
            metrics["immediate_max_coefficient_jump"] / 240 + 1e-12,
        )


if __name__ == "__main__":
    unittest.main()
