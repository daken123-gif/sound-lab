#!/usr/bin/env python3
"""Compare hard and duration-adaptive Capture loop boundaries.

This deterministic audio experiment tests a design hypothesis. It is not a
reconstruction of Chroma Console firmware or its proprietary Capture process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


FS = 48_000


def test_capture(duration_s: float, kind: str) -> np.ndarray:
    count = int(round(duration_s * FS))
    time = np.arange(count, dtype=np.float64) / FS
    phase = duration_s and time / duration_s

    if kind == "short":
        envelope = (1.0 - np.exp(-time / 0.002)) * (0.34 + 0.66 * np.exp(-time / 0.11))
        signal = envelope * (
            0.58 * np.sin(2.0 * np.pi * 223.0 * time + 0.31)
            + 0.25 * np.sin(2.0 * np.pi * 337.0 * time + 1.07)
        )
    elif kind == "medium":
        envelope = 0.42 + 0.38 * np.sin(np.pi * phase) ** 2
        signal = envelope * (
            0.52 * np.sin(2.0 * np.pi * 146.8 * time + 0.42)
            + 0.20 * np.sin(2.0 * np.pi * 293.6 * time + 0.91)
            + 0.11 * np.sin(2.0 * np.pi * 587.2 * time + 0.13)
        )
    elif kind == "long":
        phrase = 0.46 + 0.34 * np.sin(np.pi * phase) ** 2
        signal = phrase * (
            0.47 * np.sin(2.0 * np.pi * 110.0 * time + 0.27)
            + 0.22 * np.sin(2.0 * np.pi * 164.8 * time + 0.76)
            + 0.14 * np.sin(2.0 * np.pi * 329.6 * time + 1.14)
        )
        for start_s in (0.31, 1.08, 1.79):
            start = int(start_s * FS)
            length = min(int(0.025 * FS), count - start)
            burst_time = np.arange(length, dtype=np.float64) / FS
            signal[start : start + length] += 0.16 * np.sin(
                2.0 * np.pi * 1730.0 * burst_time
            ) * np.exp(-burst_time / 0.007)
    else:
        raise ValueError(kind)
    return signal


def adaptive_fade_ms(duration_s: float) -> float:
    """Proposed policy: substantial overlap for grains, tiny seam for phrases."""
    if duration_s <= 0.35:
        return min(60.0, duration_s * 250.0)  # 25% of the capture.
    if duration_s <= 1.2:
        return 30.0
    return 10.0


def overlap_loop(source: np.ndarray, fade_ms: float) -> np.ndarray:
    """Overlap the release with the attack and shorten playback by that overlap."""
    fade = int(round(fade_ms * 0.001 * FS))
    if fade < 2 or fade * 2 >= source.size:
        raise ValueError("crossfade must be at least two samples and below half the capture")
    weight = np.linspace(0.0, 1.0, fade, endpoint=True)
    blended = source[-fade:] * (1.0 - weight) + source[:fade] * weight
    return np.concatenate((source[fade:-fade], blended))


def seam_metrics(loop: np.ndarray) -> dict:
    ordinary_steps = np.abs(np.diff(loop))
    seam_jump = abs(float(loop[0] - loop[-1]))
    median_step = float(np.median(ordinary_steps))
    return {
        "seam_jump": seam_jump,
        "median_ordinary_step": median_step,
        "seam_to_median_step_ratio": seam_jump / (median_step + 1e-15),
    }


def seam_high_band_fraction(loop: np.ndarray, window_ms: float = 20.0) -> float:
    half = int(round(window_ms * 0.0005 * FS))
    segment = np.concatenate((loop[-half:], loop[:half]))
    spectrum = np.abs(np.fft.rfft(segment * np.hanning(segment.size))) ** 2
    frequency = np.fft.rfftfreq(segment.size, 1.0 / FS)
    return float(np.sum(spectrum[frequency >= 8_000.0]) / (np.sum(spectrum) + 1e-30))


def analyze(duration_s: float, kind: str) -> dict:
    source = test_capture(duration_s, kind)
    fade_ms = adaptive_fade_ms(duration_s)
    processed = overlap_loop(source, fade_ms)
    hard = seam_metrics(source)
    soft = seam_metrics(processed)
    return {
        "raw_duration_s": duration_s,
        "fixed_120ms_overlap_fraction_percent": 100.0 * 0.120 / duration_s,
        "fixed_120ms_valid_under_half_capture": 0.120 < duration_s * 0.5,
        "adaptive_overlap_ms": fade_ms,
        "overlap_fraction_percent": 100.0 * (fade_ms * 0.001) / duration_s,
        "processed_loop_duration_s": processed.size / FS,
        "hard_boundary": hard,
        "adaptive_boundary": soft,
        "seam_jump_reduction_db": 20.0 * np.log10(
            (hard["seam_jump"] + 1e-15) / (soft["seam_jump"] + 1e-15)
        ),
        "hard_seam_high_band_fraction": seam_high_band_fraction(source),
        "adaptive_seam_high_band_fraction": seam_high_band_fraction(processed),
    }


def run() -> dict:
    cases = {
        "short_180ms": analyze(0.180, "short"),
        "medium_650ms": analyze(0.650, "medium"),
        "long_2400ms": analyze(2.400, "long"),
    }
    return {
        "model": "duration-adaptive Capture boundary hypothesis",
        "not_hardware_emulation": True,
        "sample_rate": FS,
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("capture-boundary-metrics.json"))
    args = parser.parse_args()
    metrics = run()
    serialized = json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    print(f"sha256={hashlib.sha256(serialized.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
