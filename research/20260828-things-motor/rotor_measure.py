#!/usr/bin/env python3
"""Offline measurements for the four-input Things Motor / Crystal Palace study.

This is deliberately UI-free.  It measures coefficient behaviour before the
rotor is allowed anywhere near the Field Looper performance surface.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass


TAU = 2.0 * math.pi


def db(amplitude: float) -> float:
    if amplitude <= 0.0:
        return float("-inf")
    return 20.0 * math.log10(amplitude)


def adjacent_pair(phase: float, track_count: int = 4) -> tuple[int, int, float]:
    """Return current track, next track, and local phase in [0, 1)."""
    if track_count < 2:
        raise ValueError("track_count must be at least 2")
    position = (phase % 1.0) * track_count
    current = int(math.floor(position)) % track_count
    local = position - math.floor(position)
    return current, (current + 1) % track_count, local


def crossfade_gains(local: float, curve: str) -> tuple[float, float]:
    """Return gains for one adjacent-track transition."""
    local = min(1.0, max(0.0, local))
    if curve == "equal_power":
        return math.cos(math.pi * local / 2.0), math.sin(math.pi * local / 2.0)
    if curve == "linear":
        return 1.0 - local, local
    raise ValueError(f"unknown curve: {curve}")


def rotor_coefficients(
    phase: float, *, track_count: int = 4, curve: str = "equal_power"
) -> list[float]:
    current, following, local = adjacent_pair(phase, track_count)
    first, second = crossfade_gains(local, curve)
    result = [0.0] * track_count
    result[current] = first
    result[following] = second
    return result


@dataclass
class Motor:
    """A phase-continuous motor with exponential speed inertia."""

    sample_rate: float = 48_000.0
    time_constant_seconds: float = 0.150
    phase: float = 0.0
    speed_hz: float = 0.0
    target_speed_hz: float = 0.0

    @property
    def smoothing(self) -> float:
        if self.time_constant_seconds <= 0.0:
            return 1.0
        return 1.0 - math.exp(
            -1.0 / (self.time_constant_seconds * self.sample_rate)
        )

    def tick(self) -> tuple[float, float]:
        self.speed_hz += self.smoothing * (self.target_speed_hz - self.speed_hz)
        self.phase = (self.phase + self.speed_hz / self.sample_rate) % 1.0
        return self.phase, self.speed_hz


def measure_curve(curve: str, steps: int = 16_384) -> dict[str, float]:
    max_power_error = 0.0
    max_amplitude_error = 0.0
    peak_correlated_gain = 0.0
    for index in range(steps + 1):
        local = index / steps
        first, second = crossfade_gains(local, curve)
        max_power_error = max(max_power_error, abs(first * first + second * second - 1.0))
        max_amplitude_error = max(max_amplitude_error, abs(first + second - 1.0))
        peak_correlated_gain = max(peak_correlated_gain, first + second)
    midpoint = sum(crossfade_gains(0.5, curve))
    return {
        "max_power_sum_error": max_power_error,
        "max_amplitude_sum_error": max_amplitude_error,
        "midpoint_correlated_gain": midpoint,
        "midpoint_correlated_gain_db": db(midpoint),
        "peak_correlated_gain": peak_correlated_gain,
        "peak_correlated_gain_db": db(peak_correlated_gain),
    }


def measure_wrap(curve: str, epsilon: float = 1.0e-9) -> dict[str, float]:
    before = rotor_coefficients(1.0 - epsilon, curve=curve)
    after = rotor_coefficients(0.0, curve=curve)
    return {
        "epsilon": epsilon,
        "max_coefficient_jump": max(abs(a - b) for a, b in zip(before, after)),
        "l1_coefficient_jump": sum(abs(a - b) for a, b in zip(before, after)),
    }


def measure_motor(
    sample_rate: float = 48_000.0,
    time_constant_seconds: float = 0.150,
    run_speed_hz: float = 2.0,
    run_seconds: float = 1.0,
    stop_seconds: float = 2.0,
) -> dict[str, float]:
    motor = Motor(
        sample_rate=sample_rate,
        time_constant_seconds=time_constant_seconds,
        target_speed_hz=run_speed_hz,
    )
    maximum_speed_step = 0.0
    previous_speed = motor.speed_hz
    for _ in range(round(run_seconds * sample_rate)):
        _, speed = motor.tick()
        maximum_speed_step = max(maximum_speed_step, abs(speed - previous_speed))
        previous_speed = speed

    speed_before_stop = motor.speed_hz
    phase_at_stop_command = motor.phase
    motor.target_speed_hz = 0.0
    first_stop_phase, first_stop_speed = motor.tick()
    maximum_speed_step = max(
        maximum_speed_step, abs(first_stop_speed - previous_speed)
    )
    previous_speed = first_stop_speed
    for _ in range(round(stop_seconds * sample_rate) - 1):
        _, speed = motor.tick()
        maximum_speed_step = max(maximum_speed_step, abs(speed - previous_speed))
        previous_speed = speed

    return {
        "sample_rate": sample_rate,
        "time_constant_seconds": time_constant_seconds,
        "run_speed_hz": run_speed_hz,
        "speed_before_stop_hz": speed_before_stop,
        "first_stop_sample_speed_hz": first_stop_speed,
        "first_stop_sample_phase_advance": (first_stop_phase - phase_at_stop_command) % 1.0,
        "residual_speed_after_stop_hz": motor.speed_hz,
        "phase_after_stop": motor.phase,
        "maximum_per_sample_speed_step_hz": maximum_speed_step,
    }


def measurement_report() -> dict[str, object]:
    return {
        "study": "20260828-things-motor",
        "track_count": 4,
        "equal_power": measure_curve("equal_power"),
        "linear": measure_curve("linear"),
        "phase_wrap_equal_power": measure_wrap("equal_power"),
        "phase_wrap_linear": measure_wrap("linear"),
        "motor": measure_motor(),
        "motor_model_defaults": asdict(Motor()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            measurement_report(),
            ensure_ascii=False,
            indent=None if args.compact else 2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
