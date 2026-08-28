#!/usr/bin/env python3
"""Phase-continuous handoff between Rotor motor and direct touch gestures."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field

from rotor_measure import Motor


def wrap01(value: float) -> float:
    return value % 1.0


def circular_delta(previous: float, current: float) -> float:
    """Return the shortest signed motion from previous to current."""
    return (current - previous + 0.5) % 1.0 - 0.5


@dataclass
class GestureRotor:
    """A single Rotor phase shared by motor motion and relative touch motion."""

    motor: Motor = field(default_factory=Motor)
    maximum_flick_hz: float = 4.0
    hold_threshold_hz: float = 0.05
    touching: bool = False
    pointer_phase: float = 0.0
    manual_velocity_hz: float = 0.0

    @property
    def phase(self) -> float:
        return self.motor.phase

    def advance_motor(self, frames: int) -> list[float]:
        if frames < 0:
            raise ValueError("frames must not be negative")
        if self.touching:
            return [self.phase] * frames
        return [self.motor.tick()[0] for _ in range(frames)]

    def begin_touch(self, pointer_phase: float) -> float:
        """Grab the current rotor position without snapping it to the finger."""
        self.touching = True
        self.pointer_phase = wrap01(pointer_phase)
        self.manual_velocity_hz = 0.0
        self.motor.speed_hz = 0.0
        self.motor.target_speed_hz = 0.0
        return self.phase

    def move_touch(self, pointer_phase: float, elapsed_seconds: float) -> list[float]:
        """Interpolate one pointer event across its audio frames."""
        if not self.touching:
            raise RuntimeError("begin_touch must be called before move_touch")
        if elapsed_seconds <= 0.0:
            raise ValueError("elapsed_seconds must be positive")
        pointer_phase = wrap01(pointer_phase)
        delta = circular_delta(self.pointer_phase, pointer_phase)
        frames = max(1, round(elapsed_seconds * self.motor.sample_rate))
        start = self.phase
        phases = [wrap01(start + delta * step / frames) for step in range(1, frames + 1)]
        self.motor.phase = phases[-1]
        actual_seconds = frames / self.motor.sample_rate
        velocity = delta / actual_seconds
        self.manual_velocity_hz = max(
            -self.maximum_flick_hz, min(self.maximum_flick_hz, velocity)
        )
        self.pointer_phase = pointer_phase
        return phases

    def end_touch(self) -> float:
        """Release into a clamped flick, or hold if motion was negligible."""
        if not self.touching:
            raise RuntimeError("no active touch")
        self.touching = False
        release_speed = self.manual_velocity_hz
        if abs(release_speed) < self.hold_threshold_hz:
            release_speed = 0.0
        self.motor.speed_hz = release_speed
        self.motor.target_speed_hz = release_speed
        return release_speed


def measurement_report() -> dict[str, float | int | str]:
    sample_rate = 48_000.0
    rotor = GestureRotor(
        motor=Motor(
            sample_rate=sample_rate,
            time_constant_seconds=0.150,
            phase=0.72,
            speed_hz=0.5,
            target_speed_hz=0.5,
        )
    )
    motor_phases = rotor.advance_motor(round(0.25 * sample_rate))
    phase_before_grab = rotor.phase
    phase_at_grab = rotor.begin_touch(0.98)
    drag_phases = rotor.move_touch(0.03, 0.050)
    phase_before_release = rotor.phase
    release_speed = rotor.end_touch()
    first_release_phase = rotor.advance_motor(1)[0]
    maximum_drag_step = max(
        abs(circular_delta(previous, current))
        for previous, current in zip([phase_at_grab, *drag_phases[:-1]], drag_phases)
    )
    return {
        "study": "20260828-things-motor-gesture",
        "sample_rate": int(sample_rate),
        "motor_phase_before_grab": phase_before_grab,
        "touch_begin_phase_jump": circular_delta(phase_before_grab, phase_at_grab),
        "pointer_motion_across_wrap": circular_delta(0.98, 0.03),
        "drag_frames": len(drag_phases),
        "maximum_per_sample_drag_phase_step": maximum_drag_step,
        "release_speed_hz": release_speed,
        "first_release_phase_step": circular_delta(phase_before_release, first_release_phase),
        "expected_release_phase_step": release_speed / sample_rate,
        "motor_frames_before_touch": len(motor_phases),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            measurement_report(),
            indent=None if args.compact else 2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
