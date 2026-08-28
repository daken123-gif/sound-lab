#!/usr/bin/env python3
"""Track-participation layouts and click-safe coefficient transitions."""

from __future__ import annotations

import argparse
import json
import math

from rotor_measure import adjacent_pair, crossfade_gains


MODES = ("skip", "hold", "hole")


def _validate_active(active: list[bool]) -> None:
    if len(active) < 2:
        raise ValueError("active must contain at least two tracks")


def sector_owners(active: list[bool], mode: str) -> list[int | None]:
    """Return the owner of every fixed sector for HOLD or HOLE.

    HOLD assigns an inactive sector to the preceding active track, wrapping
    around the circle. HOLE leaves it silent. SKIP has no fixed ownership.
    """
    _validate_active(active)
    if mode == "skip":
        raise ValueError("skip redistributes active tracks and has no fixed sectors")
    if mode == "hole":
        return [index if enabled else None for index, enabled in enumerate(active)]
    if mode != "hold":
        raise ValueError(f"unknown mode: {mode}")

    enabled = [index for index, value in enumerate(active) if value]
    if not enabled:
        return [None] * len(active)
    owners: list[int | None] = []
    for sector in range(len(active)):
        preceding = [index for index in enabled if index <= sector]
        owners.append(preceding[-1] if preceding else enabled[-1])
    return owners


def layout_coefficients(
    phase: float,
    active: list[bool],
    mode: str,
    curve: str = "equal_power",
) -> list[float]:
    """Map rotor phase to one coefficient per physical track."""
    _validate_active(active)
    if mode not in MODES:
        raise ValueError(f"unknown mode: {mode}")
    coefficients = [0.0] * len(active)
    enabled = [index for index, value in enumerate(active) if value]
    if not enabled:
        return coefficients
    if len(enabled) == 1:
        coefficients[enabled[0]] = 1.0
        return coefficients

    if mode == "skip":
        current, following, local = adjacent_pair(phase, len(enabled))
        first, second = crossfade_gains(local, curve)
        coefficients[enabled[current]] = first
        coefficients[enabled[following]] = second
        return coefficients

    owners = sector_owners(active, mode)
    current, following, local = adjacent_pair(phase, len(active))
    first_owner = owners[current]
    second_owner = owners[following]
    first, second = crossfade_gains(local, curve)

    if first_owner == second_owner and first_owner is not None:
        # A held track spanning adjacent sectors is a dwell, not two copies
        # mixed together. Summing equal-power gains here would add up to +3 dB.
        coefficients[first_owner] = 1.0
        return coefficients
    if first_owner is not None:
        coefficients[first_owner] += first
    if second_owner is not None:
        coefficients[second_owner] += second
    return coefficients


def coefficient_ramp(
    previous: list[float], target: list[float], frames: int
) -> list[list[float]]:
    """Return a linear state-change ramp, excluding the already-played start."""
    if len(previous) != len(target):
        raise ValueError("coefficient vectors must have equal length")
    if frames < 1:
        raise ValueError("frames must be positive")
    return [
        [start + (end - start) * step / frames for start, end in zip(previous, target)]
        for step in range(1, frames + 1)
    ]


def transition_metrics(
    phase: float,
    before: list[bool],
    after: list[bool],
    mode: str,
    ramp_frames: int = 240,
) -> dict[str, float | int | str]:
    old = layout_coefficients(phase, before, mode)
    new = layout_coefficients(phase, after, mode)
    immediate = max(abs(a - b) for a, b in zip(old, new))
    ramp = coefficient_ramp(old, new, ramp_frames)
    vectors = [old, *ramp]
    per_sample = max(
        abs(current - prior)
        for prior_vector, current_vector in zip(vectors, vectors[1:])
        for prior, current in zip(prior_vector, current_vector)
    )
    return {
        "mode": mode,
        "phase": phase,
        "ramp_frames": ramp_frames,
        "immediate_max_coefficient_jump": immediate,
        "ramped_max_per_sample_coefficient_jump": per_sample,
    }


def measurement_report() -> dict[str, object]:
    before = [True, True, True, True]
    after = [True, True, True, False]
    phases = [index / 4096 for index in range(4096)]
    return {
        "study": "20260828-things-motor-layout",
        "toggle": {"before": before, "after": after},
        "fixed_phase_transition": [
            transition_metrics(0.10, before, after, mode) for mode in MODES
        ],
        "worst_immediate_jump_over_circle": {
            mode: max(
                transition_metrics(phase, before, after, mode)[
                    "immediate_max_coefficient_jump"
                ]
                for phase in phases
            )
            for mode in MODES
        },
        "unaffected_fixed_arc_max_jump": {
            mode: max(
                transition_metrics(phase, before, after, mode)[
                    "immediate_max_coefficient_jump"
                ]
                for phase in phases[:2049]
            )
            for mode in MODES
        },
        "hold_owners": sector_owners(after, "hold"),
        "hole_owners": sector_owners(after, "hole"),
        "ramp": {"sample_rate": 48_000, "frames": 240, "milliseconds": 5.0},
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
