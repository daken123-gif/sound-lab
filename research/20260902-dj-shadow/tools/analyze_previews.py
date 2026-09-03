#!/usr/bin/env python3
"""Extract only calibration-approved measurements from short music previews."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from calibrate_analyzer import (
    SR,
    frame_rms,
    onset_times,
    periodicity_candidates,
    rms_dbfs,
    spectral_centroid,
    stereo_balance,
)


def decode(path: Path) -> np.ndarray:
    command = [
        "ffmpeg", "-v", "error", "-i", str(path),
        "-f", "f32le", "-acodec", "pcm_f32le", "-ar", str(SR), "-ac", "2", "-",
    ]
    raw = subprocess.check_output(command)
    audio = np.frombuffer(raw, dtype="<f4")
    if len(audio) % 2:
        raise ValueError(f"odd stereo sample count: {path}")
    return audio.reshape(-1, 2).astype(np.float64)


def finite(value: float, digits: int = 4) -> float | None:
    return round(float(value), digits) if np.isfinite(value) else None


def analyze(path: Path) -> dict[str, object]:
    audio = decode(path)
    duration = len(audio) / SR
    onsets = onset_times(audio, SR)
    intervals = np.diff(onsets)
    rms_frames = frame_rms(audio)
    rms_frames_db = 20.0 * np.log10(np.maximum(rms_frames, 1e-15))
    candidates = periodicity_candidates(audio, SR)
    return {
        "file": path.name,
        "duration_s": finite(duration),
        "rms_dbfs": finite(rms_dbfs(audio), 2),
        "frame_rms_dbfs_p10_p50_p90": [finite(np.percentile(rms_frames_db, p), 2) for p in (10, 50, 90)],
        "spectral_centroid_hz": finite(spectral_centroid(audio, SR), 1),
        "stereo_balance_minus_left_plus_right": finite(stereo_balance(audio), 4),
        "onset_count": int(len(onsets)),
        "onsets_per_second": finite(len(onsets) / duration, 3),
        "onset_interval_median_s": finite(np.median(intervals), 4) if len(intervals) else None,
        "onset_interval_cv": finite(np.std(intervals) / np.mean(intervals), 3) if len(intervals) else None,
        "periodicity_candidates_bpm": [finite(value, 2) for value in candidates[:8]],
        "scope": "unknown-position 30-second excerpt; periodicity is not asserted as musical beat",
    }


def main(arguments: list[str]) -> int:
    if not arguments:
        raise SystemExit("usage: analyze_previews.py FILE...")
    paths = [Path(argument) for argument in arguments]
    report = {
        "sample_rate": SR,
        "measurement_class": "calibration-approved excerpt measurements",
        "tracks": [analyze(path) for path in paths],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
