#!/usr/bin/env python3
"""Test an effect-specific DRIFT macro against a generic random LFO.

This is a deterministic control-domain research model, not a reconstruction
of Chroma Console DSP.  One normalized macro is translated into three
different kinds of behavior: continuous stereo motion, repeat-indexed decay,
and rare discrete playback-speed events.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


CONTROL_HZ = 100
DURATION_S = 60
SEED = 20260828
DRIFT_LEVELS = (0.2, 0.5, 0.8)


def smooth_noise(rng: np.random.Generator, size: int, width: int) -> np.ndarray:
    noise = rng.standard_normal(size + width - 1)
    window = np.hanning(width)
    window /= np.sum(window)
    result = np.convolve(noise, window, mode="valid")
    result -= np.mean(result)
    peak = np.max(np.abs(result))
    return result / peak if peak else result


def vibrato_model(drift: float, time: np.ndarray, rng: np.random.Generator) -> dict:
    """Map DRIFT to waveform irregularity and stereo divergence."""
    sine = np.sin(2.0 * np.pi * 0.83 * time)
    shared = smooth_noise(rng, time.size, CONTROL_HZ * 3)
    left_noise = 0.72 * shared + 0.28 * smooth_noise(rng, time.size, CONTROL_HZ * 2)
    right_noise = 0.72 * shared + 0.28 * smooth_noise(rng, time.size, CONTROL_HZ * 2)

    irregularity = drift**1.4
    divergence = drift**1.8
    depth_cents = 3.0 + 17.0 * drift
    left = depth_cents * ((1.0 - irregularity) * sine + irregularity * left_noise)
    right = depth_cents * (
        (1.0 - irregularity) * sine
        + irregularity * ((1.0 - divergence) * shared + divergence * right_noise)
    )
    random_component = left - depth_cents * (1.0 - irregularity) * sine
    return {
        "depth_cents": depth_cents,
        "random_component_rms_cents": float(np.sqrt(np.mean(random_component**2))),
        "left_right_correlation": float(np.corrcoef(left, right)[0, 1]),
        "left_right_difference_rms_cents": float(np.sqrt(np.mean((left - right) ** 2))),
    }


def reels_model(drift: float, time: np.ndarray, rng: np.random.Generator) -> dict:
    """Map DRIFT to continuous wow plus degradation accumulated per recycle."""
    repeat_count = 12
    repeats = np.arange(repeat_count + 1, dtype=np.float64)
    loss_per_repeat_db = 0.12 + 1.75 * drift**1.2
    brightness_loss_per_repeat_db = 0.18 + 2.60 * drift**1.35
    amplitude_db = -loss_per_repeat_db * repeats
    brightness_db = -brightness_loss_per_repeat_db * repeats

    wow = (0.35 + 2.8 * drift**1.25) * (
        0.76 * np.sin(2.0 * np.pi * 0.47 * time + 0.2)
        + 0.24 * smooth_noise(rng, time.size, CONTROL_HZ * 4)
    )
    return {
        "wow_rms_cents": float(np.sqrt(np.mean(wow**2))),
        "repeat_loss_db_per_cycle": loss_per_repeat_db,
        "brightness_loss_db_per_cycle": brightness_loss_per_repeat_db,
        "amplitude_after_12_repeats_db": float(amplitude_db[-1]),
        "brightness_after_12_repeats_db": float(brightness_db[-1]),
    }


def collage_model(drift: float, time: np.ndarray, rng: np.random.Generator) -> dict:
    """Map DRIFT to rare, stateful double-speed/half-speed readout events."""
    state = np.ones(time.size, dtype=np.float64)
    event_rate_hz = 0.006 + 0.145 * drift**3.0
    refractory_samples = int((1.15 - 0.35 * drift) * CONTROL_HZ)
    next_allowed = 0
    starts: list[int] = []
    durations: list[float] = []
    speeds: list[float] = []

    for index in range(time.size):
        if index < next_allowed:
            continue
        if rng.random() < event_rate_hz / CONTROL_HZ:
            duration_s = float(rng.uniform(0.25, 0.55 + 0.75 * drift))
            duration_samples = max(1, int(round(duration_s * CONTROL_HZ)))
            speed = 2.0 if rng.random() < 0.76 else 0.5
            end = min(time.size, index + duration_samples)
            state[index:end] = speed
            starts.append(index)
            durations.append((end - index) / CONTROL_HZ)
            speeds.append(speed)
            next_allowed = end + refractory_samples

    gaps = np.diff(np.asarray(starts, dtype=np.float64)) / CONTROL_HZ if len(starts) > 1 else np.array([])
    return {
        "target_event_rate_hz": event_rate_hz,
        "event_count": len(starts),
        "event_occupancy_percent": float(100.0 * np.mean(state != 1.0)),
        "mean_event_duration_s": float(np.mean(durations)) if durations else 0.0,
        "minimum_start_gap_s": float(np.min(gaps)) if gaps.size else None,
        "double_speed_events": int(sum(speed == 2.0 for speed in speeds)),
        "half_speed_events": int(sum(speed == 0.5 for speed in speeds)),
    }


def generic_lfo_model(drift: float, time: np.ndarray, rng: np.random.Generator) -> dict:
    """Reference model: the same continuous mono random signal for every effect."""
    signal = drift * smooth_noise(rng, time.size, CONTROL_HZ * 3)
    return {
        "control_rms": float(np.sqrt(np.mean(signal**2))),
        "left_right_correlation": 1.0,
        "repeat_indexed_degradation_db_per_cycle": 0.0,
        "discrete_speed_event_count": 0,
        "has_discrete_state": False,
    }


def run() -> dict:
    time = np.arange(CONTROL_HZ * DURATION_S, dtype=np.float64) / CONTROL_HZ
    results: dict[str, dict] = {}
    for level_index, drift in enumerate(DRIFT_LEVELS):
        # Separate reproducible streams prevent one model from changing another.
        base_seed = SEED + level_index * 100
        results[f"{drift:.1f}"] = {
            "vibrato": vibrato_model(drift, time, np.random.default_rng(base_seed + 1)),
            "reels": reels_model(drift, time, np.random.default_rng(base_seed + 2)),
            "collage": collage_model(drift, time, np.random.default_rng(base_seed + 3)),
            "generic_lfo": generic_lfo_model(drift, time, np.random.default_rng(base_seed + 4)),
        }

    low = results["0.2"]
    high = results["0.8"]
    comparisons = {
        "vibrato_random_rms_high_to_low": high["vibrato"]["random_component_rms_cents"]
        / low["vibrato"]["random_component_rms_cents"],
        "vibrato_stereo_difference_high_to_low": high["vibrato"]["left_right_difference_rms_cents"]
        / low["vibrato"]["left_right_difference_rms_cents"],
        "reels_repeat_loss_high_to_low": high["reels"]["repeat_loss_db_per_cycle"]
        / low["reels"]["repeat_loss_db_per_cycle"],
        "collage_occupancy_high_minus_low_percentage_points": high["collage"]["event_occupancy_percent"]
        - low["collage"]["event_occupancy_percent"],
    }
    return {
        "model": "effect-specific DRIFT control-domain hypothesis",
        "not_hardware_emulation": True,
        "seed": SEED,
        "control_hz": CONTROL_HZ,
        "duration_s": DURATION_S,
        "levels": results,
        "comparisons": comparisons,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("effect-specific-drift-metrics.json"))
    args = parser.parse_args()
    metrics = run()
    serialized = json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    print(f"sha256={hashlib.sha256(serialized.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
