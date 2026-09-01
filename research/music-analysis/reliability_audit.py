#!/usr/bin/env python3
"""Audit temporal stability of BPM and key estimates on 30-second previews."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import essentia.standard as es
import numpy as np


SR = 44_100


def bpm(audio: np.ndarray, method: str = "multifeature") -> tuple[float, float]:
    value, _, confidence, _, _ = es.RhythmExtractor2013(method=method)(audio)
    return float(value), float(confidence)


def pulse_family(values: list[float]) -> list[float]:
    normalized = []
    for value in values:
        while value < 80.0:
            value *= 2.0
        while value > 160.0:
            value /= 2.0
        normalized.append(value)
    return normalized


def classify_bpm(values: list[float]) -> tuple[str, float, float]:
    raw_cv = float(np.std(values) / np.mean(values))
    family = pulse_family(values)
    family_cv = float(np.std(family) / np.mean(family))
    if raw_cv <= 0.04:
        label = "direct_stable"
    elif family_cv <= 0.04:
        label = "half_double_stable"
    else:
        label = "unstable"
    return label, raw_cv, family_cv


def classify_key(values: list[str]) -> tuple[str, str | None]:
    count = Counter(values)
    candidate, occurrences = count.most_common(1)[0]
    if occurrences == len(values):
        return "stable", candidate
    if occurrences >= 2:
        return "partial", candidate
    return "unstable", None


def audit(path: Path) -> dict[str, object]:
    audio = es.MonoLoader(filename=str(path), sampleRate=SR)()
    full_multi, confidence = bpm(audio, "multifeature")
    full_degara, _ = bpm(audio, "degara")
    window_bpms: list[float] = []
    window_keys: list[str] = []
    key_strengths: list[float] = []
    for start_s in (0, 10, 20):
        window = audio[start_s * SR : min((start_s + 10) * SR, len(audio))]
        value, _ = bpm(window)
        key, scale, strength = es.KeyExtractor(profileType="edma")(window)
        window_bpms.append(value)
        window_keys.append(f"{key} {scale}")
        key_strengths.append(float(strength))
    bpm_class, raw_cv, family_cv = classify_bpm(window_bpms)
    key_class, key_candidate = classify_key(window_keys)
    method_diff = min(
        abs(full_multi - full_degara),
        abs(full_multi - full_degara * 2.0),
        abs(full_multi - full_degara / 2.0),
    ) / max(full_multi, 1e-9)
    return {
        "file": path.name,
        "full_bpm_multifeature": round(full_multi, 2),
        "full_bpm_degara": round(full_degara, 2),
        "multifeature_confidence": round(confidence, 3),
        "method_family_difference": round(method_diff, 4),
        "window_bpms": [round(value, 2) for value in window_bpms],
        "bpm_class": bpm_class,
        "bpm_raw_cv": round(raw_cv, 3),
        "bpm_family_cv": round(family_cv, 3),
        "window_keys": window_keys,
        "key_strengths": [round(value, 3) for value in key_strengths],
        "key_class": key_class,
        "key_candidate": key_candidate,
    }


def main(arguments: list[str]) -> int:
    tracks = [audit(Path(argument)) for argument in arguments]
    bpm_counts = Counter(track["bpm_class"] for track in tracks)
    key_counts = Counter(track["key_class"] for track in tracks)
    low_confidence = sum(float(track["multifeature_confidence"]) < 1.5 for track in tracks)
    method_disagreement = sum(float(track["method_family_difference"]) > 0.03 for track in tracks)
    report = {
        "sample_size": len(tracks),
        "bpm_class_counts": dict(bpm_counts),
        "key_class_counts": dict(key_counts),
        "full_bpm_low_confidence_below_1_5": low_confidence,
        "full_bpm_method_disagreement_over_3_percent": method_disagreement,
        "tracks": tracks,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
