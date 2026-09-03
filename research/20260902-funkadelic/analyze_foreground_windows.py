#!/usr/bin/env python3
"""Locate short-window changes without identifying instruments or song sections."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

MUSIC_ANALYSIS = Path(__file__).resolve().parents[1] / "music-analysis"
sys.path.insert(0, str(MUSIC_ANALYSIS))

from analyze_previews import decode  # noqa: E402
from calibrate_analyzer import (  # noqa: E402
    SR,
    onset_times,
    rms_dbfs,
    spectral_centroid,
    stereo_balance,
)


WINDOW_S = 2.5


def finite(value: float, digits: int = 4) -> float | None:
    return round(float(value), digits) if np.isfinite(value) else None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pcm_sha256(audio: np.ndarray) -> str:
    pcm = audio.astype("<f4", copy=False).tobytes(order="C")
    return hashlib.sha256(pcm).hexdigest()


def analyze(path: Path) -> dict[str, object]:
    audio = decode(path)
    duration_s = len(audio) / SR
    global_onsets = onset_times(audio, SR)
    windows = []

    for start_s in np.arange(0.0, duration_s, WINDOW_S):
        end_s = min(float(start_s + WINDOW_S), duration_s)
        start = int(round(float(start_s) * SR))
        end = min(int(round(end_s * SR)), len(audio))
        excerpt = audio[start:end]
        onset_count = int(np.sum((global_onsets >= start_s) & (global_onsets < end_s)))
        windows.append(
            {
                "preview_window_s": [finite(start_s, 3), finite(end_s, 3)],
                "rms_dbfs": finite(rms_dbfs(excerpt), 2),
                "spectral_centroid_hz": finite(spectral_centroid(excerpt, SR), 1),
                "stereo_balance_minus_left_plus_right": finite(
                    stereo_balance(excerpt), 4
                ),
                "global_detector_onset_count": onset_count,
            }
        )

    transitions = []
    for before, after in zip(windows, windows[1:]):
        transitions.append(
            {
                "boundary_s": after["preview_window_s"][0],
                "delta_rms_db": finite(after["rms_dbfs"] - before["rms_dbfs"], 2),
                "delta_spectral_centroid_hz": finite(
                    after["spectral_centroid_hz"]
                    - before["spectral_centroid_hz"],
                    1,
                ),
                "delta_stereo_balance": finite(
                    after["stereo_balance_minus_left_plus_right"]
                    - before["stereo_balance_minus_left_plus_right"],
                    4,
                ),
                "delta_onset_count": (
                    after["global_detector_onset_count"]
                    - before["global_detector_onset_count"]
                ),
            }
        )

    rankings = {}
    for key in (
        "delta_rms_db",
        "delta_spectral_centroid_hz",
        "delta_stereo_balance",
        "delta_onset_count",
    ):
        rankings[f"largest_absolute_{key}"] = sorted(
            transitions,
            key=lambda item: abs(item[key]),
            reverse=True,
        )[:3]

    return {
        "file": path.name,
        "container_sha256": file_sha256(path),
        "decoded_pcm_f32le_stereo_44100_sha256": pcm_sha256(audio),
        "duration_s": finite(duration_s),
        "window_s": WINDOW_S,
        "windows": windows,
        "adjacent_transitions": transitions,
        "rankings": rankings,
    }


def main(arguments: list[str]) -> int:
    if not arguments:
        raise SystemExit("usage: analyze_foreground_windows.py FILE...")
    result = {
        "measurement_class": (
            "calibration-approved measurements in shorter windows; "
            "transition ranking is exploratory"
        ),
        "tracks": [analyze(Path(argument)) for argument in arguments],
        "hard_limits": [
            "Apple preview source position is unknown",
            "short-window changes do not identify instruments, voices, or arrangement roles",
            "ranking is by absolute single-feature change, not perceptual importance",
            "onsets are counted from one globally normalized detector pass",
            "30-second excerpts do not establish full-song form",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
