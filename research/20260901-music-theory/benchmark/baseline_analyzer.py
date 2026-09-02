#!/usr/bin/env python3
"""Audio-only baseline for the first four relational benchmark cases.

This intentionally returns several periodic hypotheses.  It is a diagnostic
baseline, not the Field Looper production analyser.
"""

from __future__ import annotations

import argparse
import json
import math
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, find_peaks, sosfilt


def load_wav(path: Path) -> tuple[int, np.ndarray]:
    with wave.open(str(path), "rb") as wav:
        if wav.getsampwidth() != 2:
            raise ValueError("baseline supports 16-bit PCM only")
        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        values = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2")
    audio = values.astype(np.float64).reshape(-1, channels) / 32768.0
    return sample_rate, audio


def onset_envelope(
    signal: np.ndarray, sample_rate: int, hop: int = 240, frame: int = 960
) -> tuple[np.ndarray, np.ndarray]:
    if signal.size < frame:
        return np.array([], dtype=float), np.array([], dtype=float)
    count = 1 + (signal.size - frame) // hop
    energy = np.empty(count, dtype=float)
    window = np.hanning(frame)
    for index in range(count):
        chunk = signal[index * hop : index * hop + frame]
        energy[index] = math.sqrt(float(np.mean((chunk * window) ** 2)))
    flux = np.maximum(0.0, np.diff(energy, prepend=energy[0]))
    scale = np.percentile(flux, 95)
    if scale > 0:
        flux = flux / scale
    times = (np.arange(count) * hop + frame / 2.0) / sample_rate
    return times, flux


def detect_onsets(
    signal: np.ndarray,
    sample_rate: int,
    minimum_spacing: float = 0.085,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    times, envelope = onset_envelope(signal, sample_rate)
    if envelope.size == 0:
        return np.array([]), np.array([]), times, envelope
    hop_seconds = times[1] - times[0]
    distance = max(1, round(minimum_spacing / hop_seconds))
    positive = envelope[envelope > 0]
    prominence = (
        max(0.01, float(np.percentile(positive, 75)) * 0.35)
        if positive.size
        else 0.01
    )
    peaks, _ = find_peaks(envelope, distance=distance, prominence=prominence)
    strengths = envelope[peaks]
    return times[peaks], strengths, times, envelope


def periodic_hypotheses(
    signal: np.ndarray,
    sample_rate: int,
    minimum_period: float = 0.24,
    maximum_period: float = 3.1,
    limit: int = 12,
) -> list[dict]:
    times, envelope = onset_envelope(signal, sample_rate)
    if envelope.size < 2:
        return []
    centered = envelope - np.mean(envelope)
    correlation = np.correlate(centered, centered, mode="full")[len(centered) - 1 :]
    overlap = np.arange(len(correlation), 0, -1)
    correlation = correlation / np.maximum(1, overlap)
    if correlation[0] > 0:
        correlation /= correlation[0]
    hop_seconds = times[1] - times[0]
    first = max(1, round(minimum_period / hop_seconds))
    last = min(len(correlation) - 1, round(maximum_period / hop_seconds))
    region = correlation[first : last + 1]
    peaks, _ = find_peaks(region, distance=max(1, round(0.08 / hop_seconds)))
    rows = []
    for peak in peaks:
        lag = first + int(peak)
        score = float(correlation[lag])
        if score <= 0:
            continue
        rows.append(
            {
                "period": round(lag * hop_seconds, 6),
                "bpm_equivalent": round(60.0 / (lag * hop_seconds), 6),
                "score": round(score, 6),
            }
        )
    rows.sort(key=lambda row: row["score"], reverse=True)
    return rows[:limit]


def estimate_phase(onsets: np.ndarray, strengths: np.ndarray, period: float) -> float | None:
    if onsets.size == 0 or period <= 0:
        return None
    angles = 2.0 * math.pi * onsets / period
    vector = np.sum(strengths * np.exp(1j * angles))
    if abs(vector) < 1e-12:
        return None
    phase = (math.atan2(vector.imag, vector.real) % (2.0 * math.pi))
    return round(float(phase * period / (2.0 * math.pi)), 6)


def band_signal(
    mono: np.ndarray, sample_rate: int, low_hz: float, high_hz: float
) -> np.ndarray:
    sos = butter(4, [low_hz, high_hz], btype="bandpass", fs=sample_rate, output="sos")
    return sosfilt(sos, mono)


def robust_tempo_curve(onsets: np.ndarray) -> dict | None:
    if onsets.size < 6:
        return None
    intervals = np.diff(onsets)
    median = float(np.median(intervals))
    keep = (intervals > median * 0.65) & (intervals < median * 1.35)
    intervals = intervals[keep]
    centers = ((onsets[:-1] + onsets[1:]) / 2.0)[keep]
    if intervals.size < 4:
        return None
    slope, intercept = np.polyfit(centers, intervals, 1)
    start_period = float(intercept + slope * centers[0])
    end_period = float(intercept + slope * centers[-1])
    return {
        "period_start": round(start_period, 6),
        "period_end": round(end_period, 6),
        "bpm_start": round(60.0 / start_period, 6),
        "bpm_end": round(60.0 / end_period, 6),
        "slope_seconds_per_second": round(float(slope), 9),
        "supporting_intervals": int(intervals.size),
    }


def align_residuals(
    reference: np.ndarray, secondary: np.ndarray, window: float = 0.075
) -> list[float]:
    residuals = []
    for event in secondary:
        if reference.size == 0:
            break
        index = int(np.argmin(np.abs(reference - event)))
        residual = float(event - reference[index])
        if abs(residual) <= window:
            residuals.append(residual)
    return residuals


def analyze(path: Path) -> dict:
    sample_rate, audio = load_wav(path)
    mono = np.mean(audio, axis=1)
    onset_times, strengths, _, _ = detect_onsets(mono, sample_rate)

    hypotheses = periodic_hypotheses(mono, sample_rate)
    for row in hypotheses:
        row["phase"] = estimate_phase(onset_times, strengths, row["period"])

    channel_rows = []
    for index in range(audio.shape[1]):
        channel_rows.append(
            {
                "channel": index,
                "period_hypotheses": periodic_hypotheses(audio[:, index], sample_rate),
            }
        )

    low = band_signal(mono, sample_rate, 100.0, 400.0)
    high = band_signal(mono, sample_rate, 800.0, 2_000.0)
    low_onsets, _, _, _ = detect_onsets(low, sample_rate)
    high_onsets, _, _, _ = detect_onsets(high, sample_rate)
    residuals = align_residuals(low_onsets, high_onsets)

    return {
        "audio": {
            "file": path.name,
            "sample_rate": sample_rate,
            "channels": int(audio.shape[1]),
            "duration": round(audio.shape[0] / sample_rate, 6),
        },
        "onsets": [round(float(value), 6) for value in onset_times],
        "period_hypotheses": hypotheses,
        "channel_analysis": channel_rows,
        "low_band_tempo_curve": robust_tempo_curve(low_onsets),
        "cross_band_timing_residuals_ms": [round(value * 1000.0, 3) for value in residuals],
        "limitations": [
            "energy_flux_onsets_only",
            "fixed_frequency_bands",
            "period_scores_are_not_probabilities",
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
