#!/usr/bin/env python3
"""Measure band-wise onset relations in an authorized Spanish Joint preview.

The result describes a mastered stereo mix. It does not isolate or attribute
events to Charlie Hunter, Questlove, D'Angelo, horns, or percussion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, stft


BANDS = {
    "low_45_180_hz": (45.0, 180.0),
    "low_mid_180_800_hz": (180.0, 800.0),
    "presence_800_3000_hz": (800.0, 3000.0),
    "high_3000_12000_hz": (3000.0, 12000.0),
}


def robust_z(values: np.ndarray) -> np.ndarray:
    median = np.median(values)
    mad = np.median(np.abs(values - median))
    return (values - median) / max(1e-12, 1.4826 * mad)


def onset_envelopes(path: Path) -> tuple[int, int, dict[str, np.ndarray]]:
    rate, audio = wavfile.read(path)
    if audio.ndim == 2:
        audio = audio.astype(np.float64).mean(axis=1)
    else:
        audio = audio.astype(np.float64)
    audio /= max(1.0, np.max(np.abs(audio)))
    frame_size, hop = 2048, 256
    frequencies, _, spectrum = stft(
        audio,
        fs=rate,
        window="hann",
        nperseg=frame_size,
        noverlap=frame_size - hop,
        nfft=frame_size,
        boundary=None,
        padded=False,
    )
    magnitude = np.log1p(80.0 * np.abs(spectrum))
    positive_flux = np.maximum(0.0, np.diff(magnitude, axis=1, prepend=magnitude[:, :1]))
    envelopes = {}
    for name, (low, high) in BANDS.items():
        selected = (frequencies >= low) & (frequencies < high)
        envelope = positive_flux[selected].mean(axis=0)
        envelopes[name] = robust_z(gaussian_filter1d(envelope, 1.0))
    return rate, hop, envelopes


def peak_times(envelope: np.ndarray, rate: int, hop: int) -> np.ndarray:
    distance = max(1, round(0.075 * rate / hop))
    peaks, _ = find_peaks(envelope, height=1.5, prominence=0.8, distance=distance)
    return peaks * hop / rate


def best_lag_ms(first: np.ndarray, second: np.ndarray, rate: int, hop: int, limit_ms: float = 120.0) -> tuple[float, float]:
    limit = round(limit_ms / 1000.0 * rate / hop)
    best_lag, best_score = 0, -1.0
    for lag in range(-limit, limit + 1):
        if lag >= 0:
            x, y = first[: len(first) - lag or None], second[lag:]
        else:
            x, y = first[-lag:], second[: len(second) + lag]
        if len(x) < 8 or np.std(x) == 0 or np.std(y) == 0:
            continue
        score = float(np.corrcoef(x, y)[0, 1])
        if score > best_score:
            best_lag, best_score = lag, score
    return best_lag * hop / rate * 1000.0, best_score


def windowed_lags(first: np.ndarray, second: np.ndarray, rate: int, hop: int) -> list[dict]:
    window = round(4.0 * rate / hop)
    step = round(2.0 * rate / hop)
    results = []
    for start in range(0, max(1, len(first) - window + 1), step):
        lag, correlation = best_lag_ms(first[start:start + window], second[start:start + window], rate, hop)
        results.append({
            "start_seconds": round(start * hop / rate, 3),
            "end_seconds": round((start + window) * hop / rate, 3),
            "best_lag_ms": round(lag, 3),
            "correlation": round(correlation, 4),
        })
    return results


def nearest_offsets(first_times: np.ndarray, second_times: np.ndarray, limit_ms: float = 120.0) -> dict:
    offsets = []
    for time in first_times:
        if len(second_times) == 0:
            break
        offset = float(second_times[np.argmin(np.abs(second_times - time))] - time) * 1000.0
        if abs(offset) <= limit_ms:
            offsets.append(offset)
    if not offsets:
        return {"count": 0}
    return {
        "count": len(offsets),
        "median_ms": round(float(np.median(offsets)), 3),
        "q25_ms": round(float(np.percentile(offsets, 25)), 3),
        "q75_ms": round(float(np.percentile(offsets, 75)), 3),
        "min_ms": round(min(offsets), 3),
        "max_ms": round(max(offsets), 3),
    }


def tempo_candidates(envelopes: dict[str, np.ndarray], rate: int, hop: int) -> list[dict]:
    combined = sum(np.maximum(0.0, values) for values in envelopes.values())
    combined -= np.mean(combined)
    correlation = np.correlate(combined, combined, mode="full")[len(combined) - 1:]
    candidates = []
    for bpm in np.arange(70.0, 140.01, 0.1):
        lag = round(60.0 / bpm * rate / hop)
        if lag < len(correlation):
            candidates.append((float(correlation[lag]), float(bpm)))
    selected = []
    for score, bpm in sorted(candidates, reverse=True):
        if all(abs(bpm - item[1]) >= 3.0 for item in selected):
            selected.append((score, bpm))
        if len(selected) == 3:
            break
    maximum = max(score for score, _ in selected)
    return [{"bpm": round(bpm, 1), "relative_score": round(score / maximum, 4)} for score, bpm in selected]


def analyze(wav_path: Path, source_path: Path | None = None) -> dict:
    rate, hop, envelopes = onset_envelopes(wav_path)
    peaks = {name: peak_times(values, rate, hop) for name, values in envelopes.items()}
    pairs = [
        ("low_45_180_hz", "low_mid_180_800_hz"),
        ("low_45_180_hz", "high_3000_12000_hz"),
        ("low_mid_180_800_hz", "high_3000_12000_hz"),
    ]
    relations = {}
    for first, second in pairs:
        lag, correlation = best_lag_ms(envelopes[first], envelopes[second], rate, hop)
        windows = windowed_lags(envelopes[first], envelopes[second], rate, hop)
        lags = [item["best_lag_ms"] for item in windows]
        relations[f"{first}__to__{second}"] = {
            "global_best_lag_ms": round(lag, 3),
            "global_correlation": round(correlation, 4),
            "windows": windows,
            "window_lag_median_ms": round(float(np.median(lags)), 3),
            "window_lag_q25_ms": round(float(np.percentile(lags, 25)), 3),
            "window_lag_q75_ms": round(float(np.percentile(lags, 75)), 3),
            "nearest_peak_offsets": nearest_offsets(peaks[first], peaks[second]),
        }
    duration = len(next(iter(envelopes.values()))) * hop / rate
    return {
        "schema_version": "sound-lab.spanish-joint-preview-analysis/v1",
        "evidence_boundary": "Thirty-second Apple Music catalog preview; mastered mix analysis only. No source separation and no event attribution to individual performers.",
        "audio": {
            "duration_seconds": round(duration, 3),
            "sample_rate": rate,
            "wav_sha256": hashlib.sha256(wav_path.read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest() if source_path else None,
        },
        "tempo_candidates": tempo_candidates(envelopes, rate, hop),
        "peak_counts": {name: len(times) for name, times in peaks.items()},
        "relations": relations,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wav", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(analyze(args.wav, args.source), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
