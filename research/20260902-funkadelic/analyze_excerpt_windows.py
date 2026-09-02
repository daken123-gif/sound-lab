#!/usr/bin/env python3
"""Measure change across three 10-second windows of short Funkadelic excerpts.

This deliberately uses only the deterministic extractors calibrated in
research/music-analysis/calibrate_analyzer.py. Periodicity candidates are not
reported as musical BPM, and Apple preview position is not inferred.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

MUSIC_ANALYSIS = Path(__file__).resolve().parents[1] / "music-analysis"
sys.path.insert(0, str(MUSIC_ANALYSIS))

from analyze_previews import decode  # noqa: E402
from calibrate_analyzer import (  # noqa: E402
    SR,
    frame_rms,
    onset_times,
    periodicity_candidates,
    rms_dbfs,
    spectral_centroid,
    stereo_balance,
)


def finite(value: float, digits: int = 4) -> float | None:
    return round(float(value), digits) if np.isfinite(value) else None


def measure(audio: np.ndarray) -> dict[str, object]:
    duration = len(audio) / SR
    onsets = onset_times(audio, SR)
    intervals = np.diff(onsets)
    frames_db = 20.0 * np.log10(np.maximum(frame_rms(audio), 1e-15))
    return {
        "duration_s": finite(duration),
        "rms_dbfs": finite(rms_dbfs(audio), 2),
        "frame_rms_dbfs_p10_p50_p90": [
            finite(np.percentile(frames_db, percentile), 2)
            for percentile in (10, 50, 90)
        ],
        "spectral_centroid_hz": finite(spectral_centroid(audio, SR), 1),
        "stereo_balance_minus_left_plus_right": finite(stereo_balance(audio), 4),
        "onset_count": int(len(onsets)),
        "onsets_per_second": finite(len(onsets) / duration, 3),
        "onset_interval_median_s": (
            finite(np.median(intervals), 4) if len(intervals) else None
        ),
        "onset_interval_cv": (
            finite(np.std(intervals) / np.mean(intervals), 3)
            if len(intervals)
            else None
        ),
        "periodicity_candidates_bpm": [
            finite(value, 2) for value in periodicity_candidates(audio, SR)[:8]
        ],
    }


def analyze(path: Path) -> dict[str, object]:
    audio = decode(path)
    windows = []
    for start_s in (0, 10, 20):
        start = start_s * SR
        end = min((start_s + 10) * SR, len(audio))
        if end <= start:
            continue
        windows.append(
            {
                "preview_window_s": [start_s, finite(end / SR)],
                **measure(audio[start:end]),
            }
        )
    return {"file": path.name, "whole_excerpt": measure(audio), "windows": windows}


def main(arguments: list[str]) -> int:
    if not arguments:
        raise SystemExit("usage: analyze_excerpt_windows.py FILE...")
    result = {
        "sample_rate": SR,
        "measurement_class": "calibration-approved excerpt/window measurements",
        "tracks": [analyze(Path(argument)) for argument in arguments],
        "hard_limits": [
            "Apple preview source position is unknown",
            "periodicity candidates are not asserted as musical beat or BPM",
            "onsets are detector events, not identified instruments or notes",
            "30-second excerpts do not establish full-song form",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
