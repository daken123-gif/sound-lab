#!/usr/bin/env python3
"""Calibrate Essentia rhythm extraction and compare five short previews."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import essentia.standard as es
import numpy as np


SR = 44_100


def clicks(events: list[tuple[float, float]], duration: float) -> np.ndarray:
    audio = np.zeros(int(duration * SR), dtype=np.float32)
    length = int(0.025 * SR)
    time = np.arange(length, dtype=np.float32) / SR
    decay = np.exp(-time * 90.0)
    for event, frequency in events:
        start = int(event * SR)
        end = min(start + length, len(audio))
        size = end - start
        if size > 0:
            audio[start:end] += 0.8 * decay[:size] * np.sin(2.0 * np.pi * frequency * time[:size])
    peak = float(np.max(np.abs(audio)))
    return audio / peak * 0.8 if peak else audio


def rhythm(audio: np.ndarray) -> dict[str, object]:
    bpm, beats, confidence, estimates, intervals = es.RhythmExtractor2013(method="multifeature")(audio)
    rounded = [round(float(value), 2) for value in estimates]
    return {
        "bpm": round(float(bpm), 2),
        "confidence": round(float(confidence), 3),
        "beat_count": int(len(beats)),
        "estimate_p10_p50_p90": [
            round(float(np.percentile(estimates, p)), 2) if len(estimates) else None for p in (10, 50, 90)
        ],
        "first_estimates": rounded[:8],
        "interval_cv": round(float(np.std(intervals) / np.mean(intervals)), 3) if len(intervals) else None,
    }


def synthetic_calibration() -> list[dict[str, object]]:
    duration = 12.0
    regular = clicks([(float(t), 1_000.0) for t in np.arange(0.5, duration - 0.1, 0.5)], duration)

    swing_events: list[tuple[float, float]] = []
    for beat in np.arange(0.5, duration - 0.5, 0.5):
        swing_events.extend([(float(beat), 900.0), (float(beat + 1.0 / 3.0), 1_300.0)])
    swing = clicks(swing_events, duration)

    poly_events = [(float(t), 850.0) for t in np.arange(0.5, duration - 0.1, 0.5)]
    poly_events += [(float(t), 1_450.0) for t in np.arange(0.5, duration - 0.1, 1.0 / 3.0)]
    polyrhythm = clicks(poly_events, duration)

    drift_intervals = np.linspace(60.0 / 100.0, 60.0 / 140.0, 24)
    drift_times = [0.5]
    for interval in drift_intervals:
        drift_times.append(drift_times[-1] + float(interval))
    drift = clicks([(event, 1_100.0) for event in drift_times], drift_times[-1] + 0.5)

    cases = [
        ("regular_120", 120.0, regular),
        ("swing_120_ratio_2_to_1", 120.0, swing),
        ("polyrhythm_120_plus_180", [120.0, 180.0], polyrhythm),
        ("tempo_drift_100_to_140", [100.0, 140.0], drift),
    ]
    return [{"case": name, "expected": expected, **rhythm(audio)} for name, expected, audio in cases]


def analyze_file(path: Path) -> dict[str, object]:
    audio = es.MonoLoader(filename=str(path), sampleRate=SR)()
    key, scale, strength = es.KeyExtractor(profileType="edma")(audio)
    onsets, onset_rate = es.OnsetRate()(audio)
    dynamic_complexity, loudness = es.DynamicComplexity()(audio)
    return {
        "file": path.name,
        "duration_s": round(len(audio) / SR, 3),
        "rhythm": rhythm(audio),
        "local_key_candidate": {"key": key, "scale": scale, "strength": round(float(strength), 3)},
        "onset_rate_per_s": round(float(onset_rate), 3),
        "dynamic_complexity": round(float(dynamic_complexity), 3),
        "loudness_db": round(float(loudness), 2),
        "scope": "unknown-position short excerpt; candidates are not whole-song facts",
    }


def main(arguments: list[str]) -> int:
    files = [Path(argument) for argument in arguments]
    report = {
        "synthetic_calibration": synthetic_calibration(),
        "previews": [analyze_file(path) for path in files],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
