#!/usr/bin/env python3
"""Verify that Delay→Cassette and Cassette→Delay are non-commutative.

This is a deterministic research model, not a Chroma Console emulation.
It renders level-matched WAV files and prints objective comparison metrics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, sosfilt


FS = 48_000
DURATION_S = 4.0


def make_test_signal(fs: int = FS, duration_s: float = DURATION_S) -> np.ndarray:
    """Create repeatable voice/chord/transient-like material."""
    sample_count = int(fs * duration_s)
    t = np.arange(sample_count, dtype=np.float64) / fs

    # A formant-like harmonic stack with a slow amplitude phrase.
    harmonic = (
        0.38 * np.sin(2 * np.pi * 110.0 * t)
        + 0.20 * np.sin(2 * np.pi * 220.0 * t + 0.3)
        + 0.13 * np.sin(2 * np.pi * 330.0 * t + 0.7)
        + 0.08 * np.sin(2 * np.pi * 880.0 * t + 1.1)
        + 0.05 * np.sin(2 * np.pi * 1760.0 * t + 0.2)
    )
    phrase = 0.35 + 0.65 * np.square(np.sin(2 * np.pi * 1.25 * t))
    signal = harmonic * phrase

    # Add three decaying transients so the delay tail can be inspected.
    rng = np.random.default_rng(20260828)
    for start_s, level in ((0.18, 0.75), (1.31, 0.62), (2.57, 0.70)):
        start = int(start_s * fs)
        length = int(0.055 * fs)
        burst_t = np.arange(length, dtype=np.float64) / fs
        burst = rng.standard_normal(length) * np.exp(-burst_t / 0.010)
        signal[start : start + length] += level * burst

    # Stop the source early so only the generated tail remains at the end.
    fade_start = int(3.05 * fs)
    fade_end = int(3.20 * fs)
    signal[fade_start:fade_end] *= np.linspace(1.0, 0.0, fade_end - fade_start)
    signal[fade_end:] = 0.0
    return np.clip(signal, -1.0, 1.0)


def feedback_delay(
    x: np.ndarray,
    fs: int = FS,
    delay_ms: float = 237.0,
    feedback: float = 0.67,
    wet: float = 0.58,
) -> np.ndarray:
    delay_samples = int(round(delay_ms * 0.001 * fs))
    y = np.zeros_like(x)
    delayed = np.zeros_like(x)
    for index in range(x.size):
        previous = delayed[index - delay_samples] if index >= delay_samples else 0.0
        delayed[index] = x[index] + feedback * previous
        y[index] = (1.0 - wet) * x[index] + wet * previous
    return y


def variable_delay(x: np.ndarray, delay_samples: np.ndarray) -> np.ndarray:
    """Fractional variable delay with linear interpolation."""
    positions = np.arange(x.size, dtype=np.float64) - delay_samples
    positions = np.clip(positions, 0.0, x.size - 2.0)
    left = positions.astype(np.int64)
    fraction = positions - left
    return x[left] * (1.0 - fraction) + x[left + 1] * fraction


def cassette(x: np.ndarray, fs: int = FS, drive: float = 2.35) -> np.ndarray:
    """Small cassette-like model used only to test processing order."""
    t = np.arange(x.size, dtype=np.float64) / fs

    # Deterministic wow + flutter changes playback position.
    wow = 0.95 * np.sin(2 * np.pi * 0.43 * t + 0.4)
    flutter = 0.16 * np.sin(2 * np.pi * 6.7 * t + 1.2)
    modulated = variable_delay(x, 8.0 + wow + flutter)

    # Pre-emphasis, asymmetric soft saturation and bandwidth loss.
    emphasized = lfilter([1.0, -0.58], [1.0], modulated)
    driven = np.tanh(drive * emphasized + 0.06) - np.tanh(0.06)
    sos = butter(3, 6_700.0, btype="lowpass", fs=fs, output="sos")
    filtered = sosfilt(sos, driven)

    # Slow deterministic level instability; no random generator is used here.
    level = 1.0 - 0.055 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.71 * t + 0.8))
    return filtered * level


def match_rms(x: np.ndarray, target_dbfs: float = -18.0) -> np.ndarray:
    rms = np.sqrt(np.mean(np.square(x)) + 1e-15)
    target = 10.0 ** (target_dbfs / 20.0)
    return x * (target / rms)


def metrics(x: np.ndarray, fs: int = FS) -> dict[str, float]:
    rms = float(np.sqrt(np.mean(np.square(x)) + 1e-15))
    peak = float(np.max(np.abs(x)))
    spectrum = np.abs(np.fft.rfft(x * np.hanning(x.size))) ** 2
    frequencies = np.fft.rfftfreq(x.size, 1.0 / fs)
    power = float(np.sum(spectrum) + 1e-15)
    centroid = float(np.sum(frequencies * spectrum) / power)
    high_ratio = float(np.sum(spectrum[frequencies >= 6_000.0]) / power)
    tail = x[int(3.20 * fs) :]
    tail_rms = float(np.sqrt(np.mean(np.square(tail)) + 1e-15))
    return {
        "rms_dbfs": 20.0 * np.log10(rms + 1e-15),
        "peak_dbfs": 20.0 * np.log10(peak + 1e-15),
        "crest_db": 20.0 * np.log10((peak + 1e-15) / (rms + 1e-15)),
        "spectral_centroid_hz": centroid,
        "energy_above_6khz_ratio": high_ratio,
        "tail_rms_dbfs": 20.0 * np.log10(tail_rms + 1e-15),
    }


def compare_order(source: np.ndarray, drive: float, feedback: float) -> dict[str, float]:
    delay_then_cassette = match_rms(
        cassette(feedback_delay(source, feedback=feedback), drive=drive)
    )
    cassette_then_delay = match_rms(
        feedback_delay(cassette(source, drive=drive), feedback=feedback)
    )
    difference = delay_then_cassette - cassette_then_delay
    difference_rms = float(np.sqrt(np.mean(np.square(difference)) + 1e-15))
    first = metrics(delay_then_cassette)
    second = metrics(cassette_then_delay)
    return {
        "drive": drive,
        "feedback": feedback,
        "cross_correlation": float(
            np.corrcoef(delay_then_cassette, cassette_then_delay)[0, 1]
        ),
        "difference_rms_dbfs": 20.0 * np.log10(difference_rms + 1e-15),
        "centroid_delta_hz": (
            first["spectral_centroid_hz"] - second["spectral_centroid_hz"]
        ),
        "high_band_ratio_a_over_b": (
            first["energy_above_6khz_ratio"]
            / (second["energy_above_6khz_ratio"] + 1e-15)
        ),
    }


def write_wav(path: Path, x: np.ndarray, fs: int = FS) -> None:
    peak = np.max(np.abs(x)) + 1e-15
    safe = x * min(1.0, 0.98 / peak)
    wavfile.write(path, fs, np.asarray(safe * 32767.0, dtype=np.int16))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    source = make_test_signal()

    delay_then_cassette = match_rms(cassette(feedback_delay(source)))
    cassette_then_delay = match_rms(feedback_delay(cassette(source)))

    files = {
        "input": output_dir / "input.wav",
        "delay_then_cassette": output_dir / "delay-then-cassette.wav",
        "cassette_then_delay": output_dir / "cassette-then-delay.wav",
    }
    write_wav(files["input"], match_rms(source))
    write_wav(files["delay_then_cassette"], delay_then_cassette)
    write_wav(files["cassette_then_delay"], cassette_then_delay)

    difference = delay_then_cassette - cassette_then_delay
    correlation = float(np.corrcoef(delay_then_cassette, cassette_then_delay)[0, 1])
    difference_rms = float(np.sqrt(np.mean(np.square(difference)) + 1e-15))

    result: dict[str, object] = {
        "sample_rate_hz": FS,
        "duration_s": DURATION_S,
        "model_boundary": "deterministic research model; not Chroma Console emulation",
        "delay_then_cassette": metrics(delay_then_cassette),
        "cassette_then_delay": metrics(cassette_then_delay),
        "cross_correlation": correlation,
        "difference_rms_dbfs": 20.0 * np.log10(difference_rms + 1e-15),
        "parameter_sweep": [
            compare_order(source, drive, feedback)
            for drive in (1.2, 2.35, 4.0)
            for feedback in (0.35, 0.67, 0.82)
        ],
        "files": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in files.items()
        },
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("rendered"))
    args = parser.parse_args()
    print(json.dumps(run(args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
