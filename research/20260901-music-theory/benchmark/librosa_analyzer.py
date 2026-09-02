#!/usr/bin/env python3
"""librosa 1.0 comparison baseline for relational benchmark cases."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import librosa
import numpy as np
from scipy.signal import find_peaks

from baseline_analyzer import (
    align_residuals,
    band_signal,
    estimate_phase,
    robust_tempo_curve,
)


HOP_LENGTH = 240


def detect_onsets(
    signal: np.ndarray, sample_rate: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    envelope = librosa.onset.onset_strength(
        y=signal,
        sr=sample_rate,
        hop_length=HOP_LENGTH,
        aggregate=np.mean,
    )
    frames = librosa.onset.onset_detect(
        onset_envelope=envelope,
        sr=sample_rate,
        hop_length=HOP_LENGTH,
        units="frames",
        backtrack=False,
        normalize=True,
    )
    times = librosa.frames_to_time(frames, sr=sample_rate, hop_length=HOP_LENGTH)
    return times, envelope[frames], envelope


def periodic_hypotheses(
    signal: np.ndarray,
    sample_rate: int,
    minimum_period: float = 0.24,
    maximum_period: float = 3.1,
    limit: int = 12,
) -> list[dict]:
    _, _, envelope = detect_onsets(signal, sample_rate)
    if envelope.size < 2:
        return []

    maximum_lag = min(
        envelope.size,
        math.ceil(maximum_period * sample_rate / HOP_LENGTH) + 1,
    )
    tempogram = librosa.feature.tempogram(
        onset_envelope=envelope,
        sr=sample_rate,
        hop_length=HOP_LENGTH,
        win_length=max(16, maximum_lag),
        center=True,
        norm=None,
    )
    scores = np.mean(tempogram, axis=1)
    if scores.size and scores[0] > 0:
        scores = scores / scores[0]

    hop_seconds = HOP_LENGTH / sample_rate
    first = max(1, round(minimum_period / hop_seconds))
    last = min(len(scores) - 1, round(maximum_period / hop_seconds))
    region = scores[first : last + 1]
    peaks, _ = find_peaks(region, distance=max(1, round(0.08 / hop_seconds)))
    rows = []
    for peak in peaks:
        lag = first + int(peak)
        score = float(scores[lag])
        if score <= 0:
            continue
        period = lag * hop_seconds
        rows.append(
            {
                "period": round(period, 6),
                "bpm_equivalent": round(60.0 / period, 6),
                "score": round(score, 6),
            }
        )
    rows.sort(key=lambda row: row["score"], reverse=True)
    return rows[:limit]


def analyze(path: Path) -> dict:
    audio, sample_rate = librosa.load(path, sr=None, mono=False)
    if audio.ndim == 1:
        channels = audio[np.newaxis, :]
    else:
        channels = audio
    mono = np.mean(channels, axis=0)

    onset_times, strengths, _ = detect_onsets(mono, sample_rate)
    hypotheses = periodic_hypotheses(mono, sample_rate)
    for row in hypotheses:
        row["phase"] = estimate_phase(onset_times, strengths, row["period"])

    channel_rows = [
        {
            "channel": index,
            "period_hypotheses": periodic_hypotheses(channel, sample_rate),
        }
        for index, channel in enumerate(channels)
    ]

    low = band_signal(mono, sample_rate, 100.0, 400.0)
    high = band_signal(mono, sample_rate, 800.0, 2_000.0)
    low_onsets, _, _ = detect_onsets(low, sample_rate)
    high_onsets, _, _ = detect_onsets(high, sample_rate)
    residuals = align_residuals(low_onsets, high_onsets)

    return {
        "engine": {"name": "librosa", "version": librosa.__version__},
        "audio": {
            "file": path.name,
            "sample_rate": int(sample_rate),
            "channels": int(channels.shape[0]),
            "duration": round(channels.shape[1] / sample_rate, 6),
        },
        "onsets": [round(float(value), 6) for value in onset_times],
        "period_hypotheses": hypotheses,
        "channel_analysis": channel_rows,
        "low_band_tempo_curve": robust_tempo_curve(low_onsets),
        "cross_band_timing_residuals_ms": [round(value * 1000.0, 3) for value in residuals],
        "shared_postprocessors": [
            "baseline_analyzer.estimate_phase",
            "baseline_analyzer.robust_tempo_curve",
            "baseline_analyzer.align_residuals",
        ],
        "limitations": [
            "librosa_onset_frontend",
            "tempogram_period_scores_are_not_probabilities",
            "fixed_frequency_bands_for_timing_residuals",
            "no_semantic_role_inference",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = [analyze(path) for path in args.audio]
    payload = results[0] if len(results) == 1 else results
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
