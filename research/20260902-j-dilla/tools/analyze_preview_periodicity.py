#!/usr/bin/env python3
"""Estimate coarse periodicity candidates from short PCM WAV excerpts.

This is a provenance-first baseline for the J Dilla research branch.  It does
not estimate microtiming and must not be used to claim per-instrument onset
offsets.  It records enough method and file metadata to reproduce a run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy import signal
from scipy.io import wavfile


METHOD_VERSION = "spectral-flux-autocorrelation-v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_mono_float(path: Path) -> tuple[int, np.ndarray]:
    sample_rate, audio = wavfile.read(path)
    if audio.ndim == 2:
        audio = audio.astype(np.float64).mean(axis=1)
    else:
        audio = audio.astype(np.float64)

    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak == 0.0:
        raise ValueError(f"silent or empty input: {path}")
    return int(sample_rate), audio / peak


def parabolic_peak(values: np.ndarray, index: int) -> tuple[float, float]:
    """Return sub-bin peak location and interpolated value."""
    if index <= 0 or index >= len(values) - 1:
        return float(index), float(values[index])
    left, center, right = values[index - 1 : index + 2]
    denominator = left - 2.0 * center + right
    if abs(float(denominator)) < 1e-15:
        return float(index), float(center)
    delta = 0.5 * float(left - right) / float(denominator)
    location = float(index) + delta
    value = float(center - 0.25 * (left - right) * delta)
    return location, value


def analyse(
    path: Path,
    *,
    min_bpm: float = 70.0,
    max_bpm: float = 130.0,
    frame_length: int = 2048,
    hop_length: int = 256,
    candidate_count: int = 5,
) -> dict[str, Any]:
    sample_rate, audio = read_mono_float(path)
    if len(audio) < frame_length * 2:
        raise ValueError(f"input is too short for analysis: {path}")

    _, _, spectrum = signal.stft(
        audio,
        fs=sample_rate,
        nperseg=frame_length,
        noverlap=frame_length - hop_length,
        boundary=None,
        padded=False,
    )
    log_magnitude = np.log1p(np.abs(spectrum))
    flux = np.maximum(np.diff(log_magnitude, axis=1), 0.0).sum(axis=0)
    flux -= flux.mean()

    autocorrelation = signal.correlate(flux, flux, mode="full", method="fft")
    autocorrelation = autocorrelation[len(flux) - 1 :]
    autocorrelation /= np.arange(len(flux), 0, -1)
    zero_lag = float(autocorrelation[0])
    if zero_lag <= 0.0:
        raise ValueError(f"no usable spectral-flux variation: {path}")
    autocorrelation /= zero_lag

    frames_per_second = sample_rate / hop_length
    min_lag = max(1, int(np.floor(60.0 * frames_per_second / max_bpm)))
    max_lag = min(
        len(autocorrelation) - 2,
        int(np.ceil(60.0 * frames_per_second / min_bpm)),
    )
    region = autocorrelation[min_lag : max_lag + 1]
    peak_indices, _ = signal.find_peaks(region)
    peak_indices = peak_indices + min_lag
    if not peak_indices.size:
        peak_indices = np.array([min_lag + int(np.argmax(region))])
    ranked = peak_indices[np.argsort(autocorrelation[peak_indices])[::-1]]

    candidates: list[dict[str, float]] = []
    for index in ranked[:candidate_count]:
        lag, score = parabolic_peak(autocorrelation, int(index))
        candidates.append(
            {
                "bpm": round(60.0 * frames_per_second / lag, 6),
                "period_seconds": round(lag / frames_per_second, 9),
                "autocorrelation_score": round(score, 9),
            }
        )

    return {
        "input": {
            "filename": path.name,
            "sha256": sha256_file(path),
            "sample_rate_hz": sample_rate,
            "sample_count": int(len(audio)),
            "duration_seconds": round(len(audio) / sample_rate, 9),
        },
        "method": {
            "name": METHOD_VERSION,
            "frame_length": frame_length,
            "hop_length": hop_length,
            "bpm_range": [min_bpm, max_bpm],
            "onset_feature": "positive spectral flux of log-magnitude STFT",
            "periodicity": "unbiased autocorrelation with parabolic peak interpolation",
        },
        "candidates": candidates,
        "scope": "coarse periodicity only; not beat tracking or microtiming",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wav", nargs="+", type=Path, help="PCM WAV file(s)")
    parser.add_argument("--min-bpm", type=float, default=70.0)
    parser.add_argument("--max-bpm", type=float, default=130.0)
    parser.add_argument("--frame-length", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--candidate-count", type=int, default=5)
    parser.add_argument("--output", type=Path, help="write JSON to this path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_bpm <= 0 or args.max_bpm <= args.min_bpm:
        raise SystemExit("invalid BPM range")
    payload = {
        "schema_version": 1,
        "analysis_scope": "short-preview baseline",
        "copyright_boundary": "audio is not embedded or redistributed",
        "results": [
            analyse(
                path,
                min_bpm=args.min_bpm,
                max_bpm=args.max_bpm,
                frame_length=args.frame_length,
                hop_length=args.hop_length,
                candidate_count=args.candidate_count,
            )
            for path in args.wav
        ],
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
