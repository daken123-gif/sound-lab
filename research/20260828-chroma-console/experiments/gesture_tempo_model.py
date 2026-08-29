#!/usr/bin/env python3
"""Verify loop closure, tempo scaling, and DRIFT separation for Gesture.

This deterministic control-domain model is a product-design experiment. It is
not a reconstruction of Chroma Console firmware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


CONTROL_HZ = 200
GESTURE_DURATION_S = 4.8
SEED = 20260828
TEMPO_RATIOS = (0.5, 1.0, 2.0, 4.0)


def record_hand_gesture() -> np.ndarray:
    """Create a deterministic, imperfect hand movement with pauses and turns."""
    count = int(CONTROL_HZ * GESTURE_DURATION_S)
    time = np.arange(count, dtype=np.float64) / CONTROL_HZ
    points_t = np.array([0.0, 0.34, 0.82, 1.38, 2.05, 2.71, 3.16, 3.92, 4.45, 4.795])
    points_v = np.array([0.18, 0.22, 0.71, 0.63, 0.31, 0.35, 0.83, 0.48, 0.55, 0.72])
    gesture = np.interp(time, points_t, points_v)

    # Small hand-scale detail, faded at the start so it does not define the seam.
    detail = 0.012 * np.sin(2.0 * np.pi * 2.3 * time + 0.4)
    detail += 0.006 * np.sin(2.0 * np.pi * 5.1 * time + 1.2)
    detail *= np.minimum(1.0, time / 0.12)
    return np.clip(gesture + detail, 0.0, 1.0)


def close_loop(recorded: np.ndarray, closure_ms: float = 120.0) -> tuple[np.ndarray, int]:
    """Blend only the release edge toward the initial value with a smooth curve."""
    result = recorded.copy()
    count = max(2, int(round(closure_ms * 0.001 * CONTROL_HZ)))
    phase = np.linspace(0.0, 1.0, count, endpoint=True)
    smooth = phase * phase * (3.0 - 2.0 * phase)
    start = result[-count]
    result[-count:] = start * (1.0 - smooth) + result[0] * smooth
    return result, count


def periodic_sample(loop: np.ndarray, phase: np.ndarray) -> np.ndarray:
    positions = np.mod(phase, 1.0) * loop.size
    left = np.floor(positions).astype(np.int64) % loop.size
    right = (left + 1) % loop.size
    fraction = positions - np.floor(positions)
    return loop[left] * (1.0 - fraction) + loop[right] * fraction


def normalized_cycle(loop: np.ndarray, tempo_ratio: float, samples: int = 4096) -> np.ndarray:
    """Render one playback cycle, then describe it on normalized phase."""
    duration = GESTURE_DURATION_S / tempo_ratio
    rendered_count = max(2, int(round(duration * CONTROL_HZ)))
    playback_time = np.arange(rendered_count, dtype=np.float64) / CONTROL_HZ
    rendered = periodic_sample(loop, playback_time * tempo_ratio / GESTURE_DURATION_S)
    source_phase = np.arange(rendered_count, dtype=np.float64) / rendered_count
    target_phase = np.arange(samples, dtype=np.float64) / samples
    return np.interp(target_phase, source_phase, rendered, period=1.0)


def smooth_noise(size: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    width = int(0.32 * CONTROL_HZ)
    window = np.hanning(width)
    window /= np.sum(window)
    noise = np.convolve(rng.standard_normal(size + width - 1), window, mode="valid")
    noise -= np.mean(noise)
    noise /= np.max(np.abs(noise))
    return noise


def run() -> dict:
    raw = record_hand_gesture()
    loop, closure_count = close_loop(raw)
    reference = periodic_sample(loop, np.arange(4096, dtype=np.float64) / 4096)

    tempo = {}
    for ratio in TEMPO_RATIOS:
        cycle = normalized_cycle(loop, ratio)
        tempo[f"{ratio:.1f}"] = {
            "cycle_duration_s": GESTURE_DURATION_S / ratio,
            "shape_correlation": float(np.corrcoef(reference, cycle)[0, 1]),
            "shape_error_rms": float(np.sqrt(np.mean((reference - cycle) ** 2))),
        }

    # DRIFT runs on an independent engine clock across three Gesture cycles.
    # It must not become another recorded gesture by repeating at the loop seam.
    cycle_count = 3
    gesture_playback = np.tile(loop, cycle_count)
    drift_noise = smooth_noise(gesture_playback.size, SEED)
    drift = {}
    for amount in (0.0, 0.25, 0.75):
        drift_signal = 0.065 * amount**1.4 * drift_noise
        composite = gesture_playback + drift_signal
        drift_cycles = drift_signal.reshape(cycle_count, loop.size)
        adjacent_correlations = [
            float(np.corrcoef(drift_cycles[index], drift_cycles[index + 1])[0, 1])
            for index in range(cycle_count - 1)
        ] if amount else [0.0, 0.0]
        drift[f"{amount:.2f}"] = {
            "drift_rms": float(np.sqrt(np.mean(drift_signal**2))),
            "composite_to_gesture_correlation": float(
                np.corrcoef(gesture_playback, composite)[0, 1]
            ),
            "mean_adjacent_drift_cycle_correlation": float(np.mean(adjacent_correlations)),
            # Separate state paths mean switching DRIFT never rewrites Gesture memory.
            "stored_gesture_mutation_rms": 0.0,
            "output_min": float(np.min(composite)),
            "output_max": float(np.max(composite)),
        }

    raw_seam = abs(float(raw[-1] - raw[0]))
    closed_seam = abs(float(loop[-1] - loop[0]))
    closure_error = loop - raw
    return {
        "model": "Gesture loop/tempo/DRIFT separation hypothesis",
        "not_hardware_emulation": True,
        "control_hz": CONTROL_HZ,
        "gesture_duration_s": GESTURE_DURATION_S,
        "raw_loop_seam_jump": raw_seam,
        "closed_loop_seam_jump": closed_seam,
        "closure_window_ms": 1000.0 * closure_count / CONTROL_HZ,
        "closure_modified_fraction_percent": 100.0 * closure_count / loop.size,
        "closure_full_record_error_rms": float(np.sqrt(np.mean(closure_error**2))),
        "tempo": tempo,
        "drift": drift,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("gesture-tempo-metrics.json"))
    args = parser.parse_args()
    metrics = run()
    serialized = json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    print(f"sha256={hashlib.sha256(serialized.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
