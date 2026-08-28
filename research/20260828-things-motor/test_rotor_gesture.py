import unittest

from rotor_gesture import GestureRotor, circular_delta
from rotor_measure import Motor


class GestureRotorTests(unittest.TestCase):
    def _rotor(self, phase: float = 0.4, speed_hz: float = 0.5) -> GestureRotor:
        return GestureRotor(
            motor=Motor(
                sample_rate=1_000.0,
                phase=phase,
                speed_hz=speed_hz,
                target_speed_hz=speed_hz,
            )
        )

    def test_touch_begin_does_not_snap_rotor_to_pointer(self) -> None:
        rotor = self._rotor(phase=0.4)
        self.assertEqual(rotor.begin_touch(0.9), 0.4)
        self.assertEqual(rotor.phase, 0.4)

    def test_drag_crosses_wrap_by_short_path(self) -> None:
        rotor = self._rotor(phase=0.4)
        rotor.begin_touch(0.98)
        phases = rotor.move_touch(0.03, 0.05)
        self.assertAlmostEqual(circular_delta(0.4, phases[-1]), 0.05)
        self.assertAlmostEqual(rotor.manual_velocity_hz, 1.0)

    def test_drag_is_interpolated_at_audio_rate(self) -> None:
        rotor = self._rotor(phase=0.4)
        rotor.begin_touch(0.2)
        phases = rotor.move_touch(0.3, 0.1)
        self.assertEqual(len(phases), 100)
        chain = [0.4, *phases]
        self.assertAlmostEqual(
            max(abs(circular_delta(a, b)) for a, b in zip(chain, chain[1:])),
            0.001,
        )

    def test_release_continues_last_manual_velocity(self) -> None:
        rotor = self._rotor(phase=0.4)
        rotor.begin_touch(0.2)
        rotor.move_touch(0.3, 0.1)
        phase_before_release = rotor.phase
        self.assertAlmostEqual(rotor.end_touch(), 1.0)
        first = rotor.advance_motor(1)[0]
        self.assertAlmostEqual(circular_delta(phase_before_release, first), 0.001)

    def test_slow_release_holds_position(self) -> None:
        rotor = self._rotor(phase=0.4)
        rotor.begin_touch(0.2)
        rotor.move_touch(0.201, 0.1)
        phase_before_release = rotor.phase
        self.assertEqual(rotor.end_touch(), 0.0)
        self.assertEqual(rotor.advance_motor(20)[-1], phase_before_release)

    def test_reverse_flick_continues_backwards(self) -> None:
        rotor = self._rotor(phase=0.4)
        rotor.begin_touch(0.1)
        rotor.move_touch(0.05, 0.05)
        before = rotor.phase
        self.assertAlmostEqual(rotor.end_touch(), -1.0)
        after = rotor.advance_motor(1)[0]
        self.assertLess(circular_delta(before, after), 0.0)

    def test_flick_speed_is_clamped(self) -> None:
        rotor = self._rotor(phase=0.4)
        rotor.begin_touch(0.1)
        rotor.move_touch(0.3, 0.001)
        self.assertEqual(rotor.end_touch(), rotor.maximum_flick_hz)


if __name__ == "__main__":
    unittest.main()
