#!/usr/bin/env python3
"""Compare This Heat alternate-version preview WAVs.

Inputs are 16-bit PCM WAV files converted to 22.05 kHz stereo. The script
does not identify music and does not claim that two previews contain the same
source-time span. It reports global measurements and a log-frequency spectral
shift estimate that can be checked against labelled playback-speed ratios.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal


BINS_PER_OCTAVE = 48
LOW_HZ = 80.0
HIGH_HZ = 8000.0


def amplitude_db(value: float, floor: float = 1e-12) -> float:
    return 20.0 * math.log10(max(value, floor))


def load_pcm(path: Path) -> tuple[int, np.ndarray]:
    with wave.open(str(path), "rb") as source:
        rate = source.getframerate()
        channels = source.getnchannels()
        width = source.getsampwidth()
        frames = source.readframes(source.getnframes())
    if width != 2:
        raise ValueError(f"{path}: expected 16-bit PCM")
    audio = np.frombuffer(frames, dtype="<i2").astype(np.float64) / 32768.0
    audio = audio.reshape(-1, channels)
    if channels == 1:
        audio = np.repeat(audio, 2, axis=1)
    return rate, audio[:, :2]


def average_spectrum(mono: np.ndarray, rate: int) -> tuple[np.ndarray, np.ndarray]:
    frequencies, power = signal.welch(
        mono, fs=rate, window="hann", nperseg=4096, noverlap=3072,
        scaling="spectrum", average="median"
    )
    grid = 2.0 ** np.arange(
        math.log2(LOW_HZ), math.log2(HIGH_HZ), 1.0 / BINS_PER_OCTAVE
    )
    interpolated = np.interp(grid, frequencies, np.log10(power + 1e-15))
    return grid, interpolated


def spectral_statistics(mono: np.ndarray, rate: int) -> tuple[float, float, float]:
    frequencies, _, spectrum = signal.stft(
        mono, fs=rate, window="hann", nperseg=2048, noverlap=1536,
        boundary=None, padded=False
    )
    magnitude = np.abs(spectrum)
    weights = np.sum(magnitude, axis=1)
    total = max(float(np.sum(weights)), 1e-12)
    centroid = float(np.sum(frequencies * weights) / total)
    cumulative = np.cumsum(weights)
    rolloff = float(frequencies[np.searchsorted(cumulative, 0.85 * cumulative[-1])])
    flatness = float(np.exp(np.mean(np.log(weights + 1e-15))) / np.mean(weights + 1e-15))
    return centroid, rolloff, flatness


def tempo_candidate(mono: np.ndarray, rate: int) -> tuple[float, float]:
    hop = 256
    _, _, spectrum = signal.stft(
        mono, fs=rate, window="hann", nperseg=1024, noverlap=1024 - hop,
        boundary=None, padded=False
    )
    energy = np.sum(np.abs(spectrum) ** 2, axis=0)
    onset = np.maximum(np.diff(np.log1p(energy), prepend=np.log1p(energy[0])), 0)
    onset -= onset.mean()
    correlation = signal.correlate(onset, onset, mode="full", method="fft")
    correlation = correlation[len(onset) - 1 :]
    min_lag = max(1, int((60.0 / 240.0) * rate / hop))
    max_lag = min(len(correlation) - 1, int((60.0 / 40.0) * rate / hop))
    search = correlation[min_lag : max_lag + 1]
    lag = min_lag + int(np.argmax(search))
    bpm = 60.0 * rate / (hop * lag)
    confidence = float(correlation[lag] / max(correlation[0], 1e-12))
    return bpm, confidence


def normalized_correlation(first: np.ndarray, second: np.ndarray) -> float:
    first = (first - first.mean()) / max(first.std(), 1e-12)
    second = (second - second.mean()) / max(second.std(), 1e-12)
    return float(np.mean(first * second))


def estimate_shift(reference: np.ndarray, target: np.ndarray) -> tuple[int, float, float]:
    max_shift = 80
    best_shift = 0
    best_correlation = -1.0
    for shift in range(-max_shift, max_shift + 1):
        if shift < 0:
            ref_slice = reference[-shift:]
            target_slice = target[:shift]
        elif shift > 0:
            ref_slice = reference[:-shift]
            target_slice = target[shift:]
        else:
            ref_slice = reference
            target_slice = target
        correlation = normalized_correlation(ref_slice, target_slice)
        if correlation > best_correlation:
            best_shift = shift
            best_correlation = correlation
    frequency_ratio = 2.0 ** (best_shift / BINS_PER_OCTAVE)
    return best_shift, frequency_ratio, best_correlation


def measure(label: str, path: Path) -> dict[str, object]:
    rate, audio = load_pcm(path)
    mono = np.mean(audio, axis=1)
    rms = math.sqrt(float(np.mean(audio**2)))
    peak = float(np.max(np.abs(audio)))
    left, right = audio[:, 0], audio[:, 1]
    mid = (left + right) / 2.0
    side = (left - right) / 2.0
    side_mid = amplitude_db(
        math.sqrt(float(np.mean(side**2))) /
        max(math.sqrt(float(np.mean(mid**2))), 1e-12)
    )
    centroid, rolloff, flatness = spectral_statistics(mono, rate)
    bpm, pulse = tempo_candidate(mono, rate)
    _, spectrum = average_spectrum(mono, rate)
    return {
        "label": label,
        "duration_seconds": len(audio) / rate,
        "rms_dbfs": amplitude_db(rms),
        "crest_db": amplitude_db(peak / max(rms, 1e-12)),
        "stereo_correlation": float(np.corrcoef(left, right)[0, 1]),
        "side_mid_db": side_mid,
        "centroid_hz": centroid,
        "rolloff_85_hz": rolloff,
        "spectral_flatness": flatness,
        "tempo_candidate_bpm": bpm,
        "pulse_confidence": pulse,
        "spectrum": spectrum,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    args = parser.parse_args()
    files = {
        "Graphic/Varispeed 16": "gv16.wav",
        "Graphic/Varispeed 33": "gv33.wav",
        "Graphic/Varispeed 45": "gv45.wav",
        "Graphic/Varispeed 78": "gv78.wav",
        "24 Track Loop": "loop24.wav",
        "Repeat": "repeat.wav",
    }
    rows = {label: measure(label, args.input_dir / filename) for label, filename in files.items()}

    metric_fields = [
        "label", "duration_seconds", "rms_dbfs", "crest_db",
        "stereo_correlation", "side_mid_db", "centroid_hz", "rolloff_85_hz",
        "spectral_flatness", "tempo_candidate_bpm", "pulse_confidence",
    ]
    metric_writer = csv.DictWriter(sys.stdout, fieldnames=metric_fields)
    metric_writer.writeheader()
    for row in rows.values():
        metric_writer.writerow({key: row[key] if key == "label" else round(float(row[key]), 4) for key in metric_fields})

    print("\ncomparison,estimated_frequency_ratio,log_spectrum_correlation,shift_bins")
    reference = rows["Graphic/Varispeed 45"]["spectrum"]
    for speed in ("16", "33", "78"):
        target = rows[f"Graphic/Varispeed {speed}"]["spectrum"]
        shift, ratio, correlation = estimate_shift(reference, target)
        print(f"{speed}_vs_45,{ratio:.6f},{correlation:.6f},{shift}")

    loop_spectrum = rows["24 Track Loop"]["spectrum"]
    repeat_spectrum = rows["Repeat"]["spectrum"]
    shift, ratio, correlation = estimate_shift(loop_spectrum, repeat_spectrum)
    print(f"repeat_vs_24_track_loop,{ratio:.6f},{correlation:.6f},{shift}")


if __name__ == "__main__":
    main()
