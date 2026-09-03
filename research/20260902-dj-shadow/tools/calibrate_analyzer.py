#!/usr/bin/env python3
"""Calibrate a minimal, deterministic audio feature extractor on known signals."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

import numpy as np
from scipy.signal import find_peaks


SR = 44_100


@dataclass
class Check:
    name: str
    expected: object
    observed: object
    tolerance: object
    passed: bool


def mono(audio: np.ndarray) -> np.ndarray:
    return audio.mean(axis=1) if audio.ndim == 2 else audio


def dominant_frequency_with_confidence(audio: np.ndarray, sr: int) -> tuple[float, float]:
    signal = mono(audio).astype(np.float64)
    signal -= signal.mean()
    windowed = signal * np.hanning(len(signal))
    magnitude = np.abs(np.fft.rfft(windowed))
    peak = int(np.argmax(magnitude[1:]) + 1)
    if 1 <= peak < len(magnitude) - 1:
        alpha, beta, gamma = magnitude[peak - 1 : peak + 2]
        denominator = alpha - 2.0 * beta + gamma
        offset = 0.5 * (alpha - gamma) / denominator if denominator else 0.0
    else:
        offset = 0.0
    frequency = float((peak + offset) * sr / len(signal))
    noise_floor = float(np.median(magnitude[1:]))
    confidence_db = float(20.0 * np.log10(max(magnitude[peak], 1e-12) / max(noise_floor, 1e-12)))
    return frequency, confidence_db


def dominant_frequency(audio: np.ndarray, sr: int) -> float:
    return dominant_frequency_with_confidence(audio, sr)[0]


def spectral_centroid(audio: np.ndarray, sr: int) -> float:
    signal = mono(audio).astype(np.float64)
    magnitude = np.abs(np.fft.rfft(signal * np.hanning(len(signal))))
    frequencies = np.fft.rfftfreq(len(signal), 1.0 / sr)
    return float(np.sum(frequencies * magnitude) / max(np.sum(magnitude), 1e-12))


def frame_rms(audio: np.ndarray, frame: int = 1024, hop: int = 256) -> np.ndarray:
    signal = mono(audio).astype(np.float64)
    if len(signal) < frame:
        signal = np.pad(signal, (0, frame - len(signal)))
    count = 1 + (len(signal) - frame) // hop
    shape = (count, frame)
    strides = (signal.strides[0] * hop, signal.strides[0])
    frames = np.lib.stride_tricks.as_strided(signal, shape=shape, strides=strides)
    return np.sqrt(np.mean(frames * frames, axis=1) + 1e-15)


def onset_envelope(audio: np.ndarray, frame: int = 1024, hop: int = 256) -> np.ndarray:
    rms = frame_rms(audio, frame, hop)
    novelty = np.maximum(0.0, np.diff(rms, prepend=rms[0]))
    scale = np.percentile(novelty, 99)
    return novelty / scale if scale > 0 else novelty


def onset_times(audio: np.ndarray, sr: int, hop: int = 256) -> np.ndarray:
    envelope = onset_envelope(audio, hop=hop)
    peaks, _ = find_peaks(
        envelope,
        height=0.12,
        prominence=0.08,
        distance=max(1, int(0.08 * sr / hop)),
    )
    return peaks * hop / sr


def regular_tempo(audio: np.ndarray, sr: int) -> float:
    times = onset_times(audio, sr)
    intervals = np.diff(times)
    return float(60.0 / np.median(intervals))


def swing_ratio(audio: np.ndarray, sr: int) -> float:
    intervals = np.diff(onset_times(audio, sr))
    trimmed = intervals[1:-1] if len(intervals) > 4 else intervals
    short = np.median(trimmed[trimmed <= np.median(trimmed)])
    long = np.median(trimmed[trimmed > np.median(trimmed)])
    return float(long / short)


def periodicity_candidates(audio: np.ndarray, sr: int, hop: int = 256) -> list[float]:
    envelope = onset_envelope(audio, hop=hop)
    envelope -= envelope.mean()
    autocorr = np.correlate(envelope, envelope, mode="full")[len(envelope) - 1 :]
    if autocorr[0] > 0:
        autocorr /= autocorr[0]
    min_lag = int((60.0 / 220.0) * sr / hop)
    max_lag = int((60.0 / 50.0) * sr / hop)
    region = autocorr[min_lag : max_lag + 1]
    peaks, props = find_peaks(region, height=0.10, prominence=0.03)
    ranked = sorted(
        ((props["peak_heights"][i], peak + min_lag) for i, peak in enumerate(peaks)),
        reverse=True,
    )
    return [float(60.0 * sr / (lag * hop)) for _, lag in ranked]


def stereo_balance(audio: np.ndarray) -> float:
    left = float(np.sqrt(np.mean(audio[:, 0] ** 2)))
    right = float(np.sqrt(np.mean(audio[:, 1] ** 2)))
    return (right - left) / max(right + left, 1e-12)


def rms_dbfs(audio: np.ndarray) -> float:
    value = float(np.sqrt(np.mean(mono(audio).astype(np.float64) ** 2)))
    return float(20.0 * np.log10(max(value, 1e-15)))


def tone(frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
    time = np.arange(int(duration * SR)) / SR
    return amplitude * np.sin(2.0 * np.pi * frequency * time)


def clicks(events: list[tuple[float, float]], duration: float) -> np.ndarray:
    audio = np.zeros(int(duration * SR), dtype=np.float64)
    click_len = int(0.025 * SR)
    local_time = np.arange(click_len) / SR
    decay = np.exp(-local_time * 90.0)
    for event_time, frequency in events:
        start = int(event_time * SR)
        end = min(start + click_len, len(audio))
        length = end - start
        if length > 0:
            audio[start:end] += 0.8 * decay[:length] * np.sin(
                2.0 * np.pi * frequency * local_time[:length]
            )
    peak = np.max(np.abs(audio))
    return audio / peak * 0.8 if peak else audio


def near(value: float, expected: float, tolerance: float) -> bool:
    return abs(value - expected) <= tolerance


def main() -> int:
    checks: list[Check] = []

    a4 = tone(440.0, 4.0)
    observed_frequency, tone_confidence = dominant_frequency_with_confidence(a4, SR)
    checks.append(Check("dominant_frequency_hz", 440.0, observed_frequency, 0.5, near(observed_frequency, 440.0, 0.5)))
    observed_centroid = spectral_centroid(a4, SR)
    checks.append(Check("spectral_centroid_hz", 440.0, observed_centroid, 5.0, near(observed_centroid, 440.0, 5.0)))
    checks.append(Check("tone_frequency_confidence_db_min", 40.0, tone_confidence, ">=", tone_confidence >= 40.0))
    observed_rms = rms_dbfs(a4)
    checks.append(Check("sine_rms_dbfs", -9.0309, observed_rms, 0.02, near(observed_rms, -9.0309, 0.02)))

    rng = np.random.default_rng(20260901)
    white_noise = rng.normal(0.0, 0.2, len(a4))
    _, noise_confidence = dominant_frequency_with_confidence(white_noise, SR)
    checks.append(Check("noise_frequency_confidence_db_max", 20.0, noise_confidence, "<", noise_confidence < 20.0))
    silence_onsets = len(onset_times(np.zeros_like(a4), SR))
    checks.append(Check("silence_onset_count", 0, silence_onsets, 0, silence_onsets == 0))

    duration = 12.0
    beat_period = 0.5
    regular_events = [(t, 1_000.0) for t in np.arange(0.5, duration - 0.1, beat_period)]
    regular = clicks(regular_events, duration)
    observed_tempo = regular_tempo(regular, SR)
    checks.append(Check("regular_tempo_bpm", 120.0, observed_tempo, 1.0, near(observed_tempo, 120.0, 1.0)))

    swing_events: list[tuple[float, float]] = []
    for beat in np.arange(0.5, duration - beat_period, beat_period):
        swing_events.append((float(beat), 900.0))
        swing_events.append((float(beat + beat_period * 2.0 / 3.0), 1_300.0))
    swing = clicks(swing_events, duration)
    observed_swing = swing_ratio(swing, SR)
    checks.append(Check("swing_long_short_ratio", 2.0, observed_swing, 0.12, near(observed_swing, 2.0, 0.12)))

    drift_intervals = np.linspace(60.0 / 100.0, 60.0 / 140.0, 24)
    drift_times = [0.5]
    for interval in drift_intervals:
        drift_times.append(drift_times[-1] + float(interval))
    drift_duration = drift_times[-1] + 0.5
    drift = clicks([(event, 1_100.0) for event in drift_times], drift_duration)
    detected = onset_times(drift, SR)
    local_bpm = 60.0 / np.diff(detected)
    early_bpm = float(np.median(local_bpm[:5]))
    late_bpm = float(np.median(local_bpm[-5:]))
    drift_ok = near(early_bpm, 100.0, 4.0) and near(late_bpm, 140.0, 5.0) and late_bpm > early_bpm
    checks.append(Check("tempo_drift_bpm", [100.0, 140.0], [early_bpm, late_bpm], [4.0, 5.0], drift_ok))

    poly_events = [(float(t), 850.0) for t in np.arange(0.5, duration - 0.1, 0.5)]
    poly_events += [(float(t), 1_450.0) for t in np.arange(0.5, duration - 0.1, 1.0 / 3.0)]
    polyrhythm = clicks(poly_events, duration)
    candidates = periodicity_candidates(polyrhythm, SR)
    has_120 = any(near(value, 120.0, 3.0) for value in candidates)
    has_180 = any(near(value, 180.0, 4.0) for value in candidates)
    checks.append(Check("polyrhythm_periodicities_bpm", [120.0, 180.0], candidates[:12], [3.0, 4.0], has_120 and has_180))

    base = tone(440.0, 2.0)
    left = np.column_stack([base, np.zeros_like(base)])
    right = np.column_stack([np.zeros_like(base), base])
    left_balance = stereo_balance(left)
    right_balance = stereo_balance(right)
    checks.append(Check("left_balance", -1.0, left_balance, 0.01, near(left_balance, -1.0, 0.01)))
    checks.append(Check("right_balance", 1.0, right_balance, 0.01, near(right_balance, 1.0, 0.01)))

    report = {
        "sample_rate": SR,
        "checks": [asdict(check) for check in checks],
        "passed": sum(check.passed for check in checks),
        "total": len(checks),
        "all_passed": all(check.passed for check in checks),
        "method_limits": [
            "periodicity candidates are not equivalent to a human musical beat",
            "polyrhythm produces valid subharmonic and multiple-tempo candidates",
            "frequency estimates require confidence-based rejection",
            "local tempo must be retained when tempo changes over time",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
