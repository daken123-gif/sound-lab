#!/usr/bin/env python3
"""Measure short original/dub previews without claiming full-track coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal


SR = 24_000
FRAME = 2048
HOP = 240


def decode(path: Path) -> np.ndarray:
    proc = subprocess.run(
        [
            "ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le",
            "-ac", "1", "-ar", str(SR), "pipe:1",
        ],
        check=True,
        stdout=subprocess.PIPE,
    )
    return np.frombuffer(proc.stdout, dtype="<f4").astype(np.float64)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stft_features(y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    freqs, _, z = signal.stft(
        y, fs=SR, window="hann", nperseg=FRAME, noverlap=FRAME - HOP,
        boundary=None, padded=False,
    )
    power = np.abs(z) ** 2 + 1e-14
    bands = np.vstack([
        power[(freqs >= 40) & (freqs < 250)].sum(axis=0),
        power[(freqs >= 250) & (freqs < 4000)].sum(axis=0),
        power[(freqs >= 4000) & (freqs < 11000)].sum(axis=0),
    ])
    total = power.sum(axis=0)
    centroid = (freqs[:, None] * power).sum(axis=0) / total
    return bands, centroid, power


def separated_peaks(values: np.ndarray, count: int = 8, min_gap_s: float = 0.65) -> list[int]:
    order = np.argsort(values)[::-1]
    chosen: list[int] = []
    min_gap = int(round(min_gap_s * SR / HOP))
    for idx in order:
        if all(abs(int(idx) - old) >= min_gap for old in chosen):
            chosen.append(int(idx))
            if len(chosen) == count:
                break
    return sorted(chosen)


def analyze(path: Path) -> dict:
    y = decode(path)
    bands, centroid, _ = stft_features(y)
    band_total = bands.sum(axis=1)
    ratios = band_total / band_total.sum()
    rms = float(np.sqrt(np.mean(y * y)))
    peak = float(np.max(np.abs(y)))

    log_bands = 10 * np.log10(bands + 1e-12)
    delta = np.linalg.norm(np.diff(log_bands, axis=1), axis=0)
    peak_frames = separated_peaks(delta)
    transitions = [
        {
            "time_s": round((idx + 1) * HOP / SR, 3),
            "change_score_db": round(float(delta[idx]), 3),
        }
        for idx in peak_frames
    ]

    return {
        "file": path.name,
        "sha256": sha256(path),
        "duration_s": round(len(y) / SR, 6),
        "sample_rate_hz": SR,
        "rms_dbfs": round(20 * np.log10(rms + 1e-15), 3),
        "peak_dbfs": round(20 * np.log10(peak + 1e-15), 3),
        "crest_db": round(20 * np.log10((peak + 1e-15) / (rms + 1e-15)), 3),
        "band_energy_ratio": {
            "40_250_hz": round(float(ratios[0]), 6),
            "250_4000_hz": round(float(ratios[1]), 6),
            "4000_11000_hz": round(float(ratios[2]), 6),
        },
        "spectral_centroid_median_hz": round(float(np.median(centroid)), 3),
        "largest_multiband_transitions": transitions,
    }


def envelope_alignment(a_path: Path, b_path: Path) -> dict:
    a = decode(a_path)
    b = decode(b_path)
    a_bands, _, _ = stft_features(a)
    b_bands, _, _ = stft_features(b)
    names = ["40_250_hz", "250_4000_hz", "4000_11000_hz"]
    matches = {}
    for name, a_band, b_band in zip(names, a_bands, b_bands):
        a_env = np.log1p(a_band)
        b_env = np.log1p(b_band)
        a_env = (a_env - a_env.mean()) / (a_env.std() + 1e-12)
        b_env = (b_env - b_env.mean()) / (b_env.std() + 1e-12)
        corr = signal.correlate(a_env, b_env, mode="full", method="fft")
        lags = signal.correlation_lags(len(a_env), len(b_env), mode="full")
        keep = np.abs(lags * HOP / SR) <= 10
        corr = corr[keep] / min(len(a_env), len(b_env))
        lags = lags[keep]
        best = int(np.argmax(corr))
        matches[name] = {
            "best_lag_s_a_relative_to_b": round(float(lags[best] * HOP / SR), 3),
            "normalized_correlation": round(float(corr[best]), 6),
        }
    return {
        "a": a_path.name,
        "b": b_path.name,
        "feature": "log-energy envelope by frequency band",
        "band_matches": matches,
        "interpretation_limit": "Band-envelope similarity only; not proof of identical master or causality.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", action="append", nargs=2, metavar=("ORIGINAL", "DUB"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    paths = [Path(p) for pair in args.pair for p in pair]
    result = {
        "scope": "Shazam/Apple Music catalog previews only",
        "files": [analyze(p) for p in paths],
        "pairs": [envelope_alignment(Path(a), Path(b)) for a, b in args.pair],
        "method": {
            "decoder": "ffmpeg mono float32",
            "analysis_sample_rate_hz": SR,
            "stft_frame": FRAME,
            "stft_hop": HOP,
            "warning": "Measurements do not substitute for listening and do not describe unpreviewed portions of a track.",
        },
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
