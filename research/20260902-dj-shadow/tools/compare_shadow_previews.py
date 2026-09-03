#!/usr/bin/env python3
"""Exploratory, excerpt-bounded comparison for DJ Shadow Apple Music previews."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks, stft

from analyze_previews import decode as decode_calibrated
from calibrate_analyzer import SR as CALIBRATED_SR, periodicity_candidates


SR = 22_050
HOP = 256
NFFT = 2048
FILES = [
    "stem-long-stem-preview.m4a",
    "stem-cops-robbers-preview.m4a",
    "napalm-scatter-preview.m4a",
    "napalm-demo-preview.m4a",
    "stem-deluxe-combined-preview.m4a",
    "napalm-deluxe-preview.m4a",
]


def decode(path: Path) -> np.ndarray:
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(path),
        "-f", "f32le", "-acodec", "pcm_f32le",
        "-ar", str(SR), "-ac", "1", "-",
    ])
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def features(x: np.ndarray) -> dict[str, np.ndarray]:
    _, _, z = stft(
        x, fs=SR, window="hann", nperseg=NFFT, noverlap=NFFT - HOP,
        boundary=None, padded=False,
    )
    mag = np.abs(z)
    logmag = np.log1p(10.0 * mag)
    flux = np.maximum(0.0, np.diff(logmag, axis=1)).mean(axis=0)
    flux = (flux - np.median(flux)) / (np.std(flux) + 1e-12)
    flux = np.maximum(0.0, flux)
    rms = np.sqrt(np.maximum(
        0.0,
        np.convolve(x * x, np.ones(NFFT) / NFFT, mode="valid")[::HOP],
    ))
    freqs = np.fft.rfftfreq(NFFT, 1.0 / SR)
    power = mag ** 2
    bands = []
    for lo, hi in [(20, 150), (150, 1000), (1000, 6000), (6000, SR / 2)]:
        mask = (freqs >= lo) & (freqs < hi)
        bands.append(power[mask].sum())
    band_ratio = np.asarray(bands) / (np.sum(bands) + 1e-12)
    return {"flux": flux, "rms": rms, "band_ratio": band_ratio}


def tempo_profile(env: np.ndarray) -> np.ndarray:
    y = env - env.mean()
    ac = np.correlate(y, y, mode="full")[len(y) - 1:]
    ac = ac / (ac[0] + 1e-12)
    min_lag = int(round((60.0 / 220.0) * SR / HOP))
    max_lag = int(round((60.0 / 45.0) * SR / HOP))
    profile = np.maximum(0.0, ac[min_lag:max_lag + 1])
    return profile / (np.linalg.norm(profile) + 1e-12)


def aligned_correlation(a: np.ndarray, b: np.ndarray, max_lag_s: float = 2.0) -> dict[str, float]:
    n = min(len(a), len(b))
    a = (a[:n] - np.mean(a[:n])) / (np.std(a[:n]) + 1e-12)
    b = (b[:n] - np.mean(b[:n])) / (np.std(b[:n]) + 1e-12)
    max_lag = int(round(max_lag_s * SR / HOP))
    best = (-2.0, 0)
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            aa, bb = a[-lag:], b[:n + lag]
        elif lag > 0:
            aa, bb = a[:n - lag], b[lag:]
        else:
            aa, bb = a, b
        if len(aa) < 50:
            continue
        corr = float(np.dot(aa, bb) / ((np.linalg.norm(aa) * np.linalg.norm(bb)) + 1e-12))
        if corr > best[0]:
            best = (corr, lag)
    return {"correlation": round(best[0], 4), "lag_s": round(best[1] * HOP / SR, 4)}


def window_summary(x: np.ndarray, start_s: float, end_s: float) -> dict[str, object]:
    part = x[int(start_s * SR):int(end_s * SR)]
    f = features(part)
    distance = max(1, int(round(0.09 * SR / HOP)))
    peaks, _ = find_peaks(f["flux"], height=1.0, distance=distance, prominence=0.35)
    rms_db = 20.0 * np.log10(np.sqrt(np.mean(part * part)) + 1e-12)
    return {
        "range_s": [start_s, end_s],
        "rms_dbfs": round(float(rms_db), 2),
        "onsets_per_second": round(float(len(peaks) / (end_s - start_s)), 3),
        "band_energy_ratio": {
            "20_150": round(float(f["band_ratio"][0]), 4),
            "150_1000": round(float(f["band_ratio"][1]), 4),
            "1000_6000": round(float(f["band_ratio"][2]), 4),
            "6000_nyquist": round(float(f["band_ratio"][3]), 4),
        },
    }


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12))


def local_periodicity(path: Path) -> list[dict[str, object]]:
    x = decode_calibrated(path)
    out = []
    for start_s, end_s in [(0.0, 10.0), (10.0, 20.0), (20.0, 29.95)]:
        part = x[int(start_s * CALIBRATED_SR):int(end_s * CALIBRATED_SR)]
        out.append({
            "range_s": [start_s, end_s],
            "candidates_bpm": [
                round(float(value), 2)
                for value in periodicity_candidates(part, CALIBRATED_SR)[:8]
            ],
        })
    return out


def boundary_candidates(x: np.ndarray) -> list[dict[str, float]]:
    starts = np.arange(0.0, 27.51, 0.5)
    rows = []
    for start_s in starts:
        part = x[int(start_s * SR):int((start_s + 2.0) * SR)]
        f = features(part)
        distance = max(1, int(round(0.09 * SR / HOP)))
        peaks, _ = find_peaks(
            f["flux"], height=1.0, distance=distance, prominence=0.35
        )
        rms_db = 20.0 * np.log10(np.sqrt(np.mean(part * part)) + 1e-12)
        rows.append([rms_db, len(peaks) / 2.0, *f["band_ratio"]])
    values = np.asarray(rows)
    z = (values - values.mean(axis=0)) / (values.std(axis=0) + 1e-12)
    novelty = np.linalg.norm(np.diff(z, axis=0), axis=1)
    peaks, _ = find_peaks(novelty, distance=4)
    ranked = sorted(peaks, key=lambda index: novelty[index], reverse=True)[:5]
    return [
        {
            "time_s": round(float(starts[index + 1]), 2),
            "novelty": round(float(novelty[index]), 3),
        }
        for index in ranked
    ]


def main() -> None:
    audio = {name: decode(Path(name)) for name in FILES}
    feat = {name: features(x) for name, x in audio.items()}
    public = {}
    for name, x in audio.items():
        public[name] = {
            "decoded_duration_s": round(len(x) / SR, 4),
            "windows": [
                window_summary(x, 0.0, 10.0),
                window_summary(x, 10.0, 20.0),
                window_summary(x, 20.0, min(29.95, len(x) / SR)),
            ],
        }

    pairs = {}
    for label, a, b in [
        ("stem_album_vs_cops_robbers", FILES[0], FILES[1]),
        ("napalm_final_vs_demo", FILES[2], FILES[3]),
        ("stem_current_vs_deluxe", FILES[0], FILES[4]),
        ("napalm_current_vs_deluxe", FILES[2], FILES[5]),
    ]:
        pairs[label] = {
            "onset_envelope_best_alignment": aligned_correlation(feat[a]["flux"], feat[b]["flux"]),
            "rms_envelope_best_alignment": aligned_correlation(feat[a]["rms"], feat[b]["rms"]),
            "tempo_profile_cosine": round(cosine(tempo_profile(feat[a]["flux"]), tempo_profile(feat[b]["flux"])), 4),
            "band_profile_cosine": round(cosine(feat[a]["band_ratio"], feat[b]["band_ratio"]), 4),
            "boundary": "exploratory similarity of unknown-position previews; not identity or lineage proof",
        }

    targets = [FILES[0], FILES[2]]
    print(json.dumps({
        "sample_rate": SR,
        "files": public,
        "comparisons": pairs,
        "local_periodicity_10s_windows": {
            name: local_periodicity(Path(name)) for name in targets
        },
        "exploratory_boundary_candidates": {
            name: boundary_candidates(audio[name]) for name in targets
        },
        "limits": [
            "long-track previews have unknown source positions",
            "the 30-second demo preview covers most, not all, of the 34.8-second catalog track",
            "window statistics do not establish full-track scene boundaries",
            "similarity metrics are exploratory and were not part of the calibrated extractor",
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
