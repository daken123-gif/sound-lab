#!/usr/bin/env python3
"""Evaluate separator outputs against the known-stem calibration fixture."""

import json
from pathlib import Path

import numpy as np
import soundfile as sf


ROOT = Path(__file__).parent


def read(path: Path) -> np.ndarray:
    audio, sr = sf.read(path, always_2d=True, dtype="float64")
    if sr != 44_100:
        raise ValueError(f"unexpected sample rate {sr}: {path}")
    return audio


def align(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = min(len(a), len(b))
    return a[:n].reshape(-1), b[:n].reshape(-1)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    a, b = align(a, b)
    den = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / den) if den else 0.0


def si_sdr(estimate: np.ndarray, target: np.ndarray) -> float:
    estimate, target = align(estimate, target)
    estimate -= estimate.mean()
    target -= target.mean()
    alpha = np.dot(estimate, target) / (np.dot(target, target) + 1e-18)
    projected = alpha * target
    noise = estimate - projected
    return float(10 * np.log10((np.dot(projected, projected) + 1e-18) / (np.dot(noise, noise) + 1e-18)))


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x))))


def evaluate(kind: str, predicted_path: Path, complement_path: Path) -> dict:
    target = read(ROOT / "fixture" / f"{kind}.wav")
    predicted = read(predicted_path)
    complement = read(complement_path)
    mixture = read(ROOT / "fixture" / "mixture.wav")
    others = {
        name: read(ROOT / "fixture" / f"{name}.wav")
        for name in ("drums", "bass", "other")
        if name != kind
    }
    n = min(map(len, [mixture, predicted, complement]))
    residual = mixture[:n] - predicted[:n] - complement[:n]
    return {
        "target": kind,
        "si_sdr_db": round(si_sdr(predicted, target), 3),
        "target_cosine": round(cosine(predicted, target), 4),
        "non_target_cosines": {name: round(cosine(predicted, audio), 4) for name, audio in others.items()},
        "predicted_rms": round(rms(predicted), 6),
        "target_rms": round(rms(target), 6),
        "reconstruction_residual_rms": round(rms(residual), 9),
    }


def main() -> None:
    results = [
        evaluate(
            "drums",
            ROOT / "separated/fixture-drums/mixture_(Drums)_kuielab_b_drums.wav",
            ROOT / "separated/fixture-drums/mixture_(No Drums)_kuielab_b_drums.wav",
        ),
        evaluate(
            "bass",
            ROOT / "separated/fixture-bass/mixture_(Bass)_kuielab_b_bass.wav",
            ROOT / "separated/fixture-bass/mixture_(No Bass)_kuielab_b_bass.wav",
        ),
    ]
    output = ROOT / "separation-fixture-results.json"
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print(output.read_text(), end="")


if __name__ == "__main__":
    main()
