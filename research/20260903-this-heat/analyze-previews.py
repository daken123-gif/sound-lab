#!/usr/bin/env python3
"""Measure short PCM WAV previews without retaining source audio.

Expected input: 22.05 kHz stereo PCM WAV. The script prints one CSV row per
file. Tempo is only a candidate derived from the onset envelope and can be a
half/double-time value.
"""

from __future__ import annotations

import argparse
import csv
import math
import wave
from pathlib import Path

import numpy as np
from scipy import signal


def db(value: float, floor: float = 1e-12) -> float:
    return 20.0 * math.log10(max(value, floor))


def load_pcm(path: Path) -> tuple[int, np.ndarray]:
    with wave.open(str(path), "rb") as wav:
        rate = wav.getframerate()
        channels = wav.getnchannels()
        width = wav.getsampwidth()
        frames = wav.readframes(wav.getnframes())
    if width != 2:
        raise ValueError(f"{path}: expected 16-bit PCM, got {width * 8}-bit")
    samples = np.frombuffer(frames, dtype="<i2").astype(np.float64) / 32768.0
    return rate, samples.reshape(-1, channels)


def centroid(mono: np.ndarray, rate: int) -> float:
    _, _, spectrum = signal.stft(
        mono, fs=rate, window="hann", nperseg=2048, noverlap=1536,
        boundary=None, padded=False
    )
    magnitude = np.abs(spectrum)
    frequencies = np.fft.rfftfreq(2048, 1.0 / rate)[:, None]
    return float(np.sum(frequencies * magnitude) / max(np.sum(magnitude), 1e-12))


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
    window = correlation[min_lag : max_lag + 1]
    lag = min_lag + int(np.argmax(window))
    bpm = 60.0 * rate / (hop * lag)
    confidence = float(correlation[lag] / max(correlation[0], 1e-12))
    return bpm, confidence


def thirds(values: np.ndarray) -> list[np.ndarray]:
    return list(np.array_split(values, 3))


def measure(path: Path) -> list[object]:
    rate, audio = load_pcm(path)
    if audio.shape[1] == 1:
        audio = np.repeat(audio, 2, axis=1)
    left, right = audio[:, 0], audio[:, 1]
    mono = (left + right) / 2.0
    mid = mono
    side = (left - right) / 2.0
    rms = math.sqrt(float(np.mean(audio**2)))
    peak = float(np.max(np.abs(audio)))
    corr = float(np.corrcoef(left, right)[0, 1])
    side_mid = db(math.sqrt(float(np.mean(side**2))) / max(math.sqrt(float(np.mean(mid**2))), 1e-12))
    bpm, confidence = tempo_candidate(mono, rate)
    rms_parts = [db(math.sqrt(float(np.mean(part**2)))) for part in thirds(audio)]
    centroid_parts = [centroid(part, rate) for part in thirds(mono)]
    return [
        path.stem, round(bpm, 1), round(confidence, 2), round(db(rms), 1),
        round(db(peak / max(rms, 1e-12)), 1), round(corr, 2),
        round(side_mid, 1), round(centroid(mono, rate)),
        *[round(value, 1) for value in rms_parts],
        *[round(value) for value in centroid_parts],
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wav", type=Path, nargs="+")
    args = parser.parse_args()
    writer = csv.writer(__import__("sys").stdout)
    writer.writerow([
        "track", "tempo_candidate_bpm", "pulse_confidence", "rms_dbfs",
        "crest_db", "stereo_correlation", "side_mid_db",
        "spectral_centroid_hz", "rms_third_1_dbfs", "rms_third_2_dbfs",
        "rms_third_3_dbfs", "centroid_third_1_hz", "centroid_third_2_hz",
        "centroid_third_3_hz",
    ])
    for path in args.wav:
        writer.writerow(measure(path))


if __name__ == "__main__":
    main()
