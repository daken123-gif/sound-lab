import math
import unittest

from rotor_measure import (
    Motor,
    adjacent_pair,
    crossfade_gains,
    measure_curve,
    measure_motor,
    measure_wrap,
    rotor_coefficients,
)


class RotorCoefficientTests(unittest.TestCase):
    def test_track_order_and_wrap(self) -> None:
        self.assertEqual(adjacent_pair(0.0), (0, 1, 0.0))
        self.assertEqual(adjacent_pair(0.25), (1, 2, 0.0))
        current, following, local = adjacent_pair(0.999)
        self.assertEqual((current, following), (3, 0))
        self.assertGreater(local, 0.99)

    def test_equal_power_invariant(self) -> None:
        result = measure_curve("equal_power")
        self.assertLess(result["max_power_sum_error"], 1.0e-12)
        self.assertAlmostEqual(
            result["midpoint_correlated_gain_db"], 3.010299956639812, places=9
        )

    def test_linear_amplitude_invariant(self) -> None:
        result = measure_curve("linear")
        self.assertLess(result["max_amplitude_sum_error"], 1.0e-12)
        self.assertAlmostEqual(result["midpoint_correlated_gain_db"], 0.0, places=12)

    def test_one_adjacent_pair_is_active(self) -> None:
        for phase in (0.0, 0.01, 0.249, 0.25, 0.51, 0.999999):
            coefficients = rotor_coefficients(phase)
            self.assertLessEqual(sum(value > 0.0 for value in coefficients), 2)
            self.assertTrue(all(math.isfinite(value) for value in coefficients))

    def test_wrap_is_continuous(self) -> None:
        for curve in ("equal_power", "linear"):
            result = measure_wrap(curve)
            self.assertLess(result["max_coefficient_jump"], 1.0e-7)

    def test_bad_curve_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            crossfade_gains(0.5, "unknown")


class MotorTests(unittest.TestCase):
    def test_stop_preserves_phase_continuity(self) -> None:
        result = measure_motor()
        self.assertGreater(result["first_stop_sample_phase_advance"], 0.0)
        self.assertLess(result["first_stop_sample_phase_advance"], 1.0e-3)
        self.assertLess(result["residual_speed_after_stop_hz"], 1.0e-5)

    def test_reverse_speed_moves_phase_backwards(self) -> None:
        motor = Motor(phase=0.5, target_speed_hz=-1.0)
        initial = motor.phase
        for _ in range(256):
            motor.tick()
        self.assertLess(motor.phase, initial)


if __name__ == "__main__":
    unittest.main()
