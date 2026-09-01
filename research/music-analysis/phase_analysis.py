#!/usr/bin/env python3
"""Calibrate rotation-invariant beat-phase measurements and compare two previews."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import essentia.standard as es
import numpy as np

from essentia_compare import SR, clicks


def phase_features(audio: np.ndarray) -> dict[str, object]:
    bpm, beats, confidence, _, _ = es.RhythmExtractor2013(method="multifeature")(audio)
    onsets, onset_rate = es.OnsetRate()(audio)
    phases: list[float] = []
    for onset in onsets:
        index = int(np.searchsorted(beats, onset) - 1)
        if 0 <= index < len(beats) - 1:
            interval = float(beats[index + 1] - beats[index])
            if interval > 0:
                phases.append(float((onset - beats[index]) / interval))
    histogram, _ = np.histogram(phases, bins=12, range=(0.0, 1.0))
    probabilities = histogram / max(histogram.sum(), 1)
    nonzero = probabilities[probabilities > 0]
    entropy = float(-np.sum(nonzero * np.log(nonzero)) / np.log(12.0)) if len(nonzero) else 0.0
    denominator = float(np.dot(histogram, histogram)) or 1.0
    circular = [float(np.dot(histogram, np.roll(histogram, lag)) / denominator) for lag in range(12)]
    centers = (np.arange(12) + 0.5) / 12.0
    top = np.argsort(histogram)[::-1][:4]
    return {
        "bpm_candidate": round(float(bpm), 2),
        "beat_confidence": round(float(confidence), 3),
        "onset_rate_per_s": round(float(onset_rate), 3),
        "phase_histogram_12": histogram.tolist(),
        "top_phase_centers": [round(float(centers[index]), 3) for index in top if histogram[index] > 0],
        "phase_entropy_0_concentrated_1_diffuse": round(entropy, 3),
        "binary_spacing_score": round(circular[6], 3),
        "triplet_spacing_score": round(max(circular[4], circular[8]), 3),
        "usable_onsets": len(phases),
    }


def synthetic() -> list[dict[str, object]]:
    duration = 12.0
    patterns: dict[str, list[tuple[float, float]]] = {"straight_eighth": [], "swing_2_to_1": [], "shifted_straight_eighth": []}
    for beat in np.arange(0.5, duration - 0.5, 0.5):
        patterns["straight_eighth"] += [(float(beat), 900.0), (float(beat + 0.25), 1_300.0)]
        patterns["swing_2_to_1"] += [(float(beat), 900.0), (float(beat + 1.0 / 3.0), 1_300.0)]
        patterns["shifted_straight_eighth"] += [(float(beat + 0.125), 900.0), (float(beat + 0.375), 1_300.0)]
    return [{"case": name, **phase_features(clicks(events, duration))} for name, events in patterns.items()]


def main(arguments: list[str]) -> int:
    previews = []
    for argument in arguments:
        path = Path(argument)
        audio = es.MonoLoader(filename=str(path), sampleRate=SR)()
        previews.append({"file": path.name, **phase_features(audio)})
    result = {
        "synthetic_calibration": synthetic(),
        "previews": previews,
        "hard_limit": "rotation-invariant phase spacing cannot identify syncopation without a verified beat/downbeat anchor",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
