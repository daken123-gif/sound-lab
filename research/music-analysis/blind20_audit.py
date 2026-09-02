#!/usr/bin/env python3
"""Blind A/B drum-stem audit for the locked 20-preview Curtis sample."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import essentia.standard as es
import numpy as np

from cross_model_audit import cosine, si_sdr
from essentia_compare import SR
from phase_analysis import phase_features
from reliability_audit import classify_bpm, pulse_family


ROOT = Path(__file__).parent


def mono(path: Path) -> np.ndarray:
    return es.MonoLoader(filename=str(path), sampleRate=SR)().astype(np.float64)


def windows(audio: np.ndarray) -> list[dict[str, object]]:
    result = []
    for start_s in (0, 10, 20):
        start = start_s * SR
        stop = min(len(audio), (start_s + 10) * SR)
        result.append({"seconds": [start_s, round(stop / SR, 3)], **phase_features(audio[start:stop].astype(np.float32))})
    return result


def bpm_family_distance(a: float, b: float) -> float:
    x, y = pulse_family([a, b])
    return abs(x - y) / max((x + y) / 2.0, 1e-9)


def classify(a_full: dict, b_full: dict, a_windows: list[dict], b_windows: list[dict]) -> tuple[str, list[str]]:
    reasons = []
    a_bpms = [float(row["bpm_candidate"]) for row in a_windows]
    b_bpms = [float(row["bpm_candidate"]) for row in b_windows]
    a_stability = classify_bpm(a_bpms)[0]
    b_stability = classify_bpm(b_bpms)[0]
    bpm_agreement = bpm_family_distance(float(a_full["bpm_candidate"]), float(b_full["bpm_candidate"])) <= 0.04
    if float(a_full["beat_confidence"]) < 1.5 or float(b_full["beat_confidence"]) < 1.5:
        reasons.append("full_excerpt_low_beat_confidence")
    if a_stability == "unstable" or b_stability == "unstable":
        reasons.append("window_bpm_unstable")
    if not bpm_agreement:
        reasons.append("a_b_bpm_family_disagreement")
    if reasons:
        return "rejected", reasons

    triplet_windows = []
    nontriplet_windows = []
    for model_windows in (a_windows, b_windows):
        triplet_windows.append(sum(
            float(row["beat_confidence"]) >= 1.5
            and float(row["triplet_spacing_score"]) >= 0.5
            and float(row["triplet_spacing_score"]) > float(row["binary_spacing_score"])
            for row in model_windows
        ))
        nontriplet_windows.append(sum(
            float(row["beat_confidence"]) >= 1.5 and float(row["triplet_spacing_score"]) <= 0.1
            for row in model_windows
        ))
    if (
        float(a_full["triplet_spacing_score"]) >= 0.5
        and float(b_full["triplet_spacing_score"]) >= 0.5
        and float(a_full["triplet_spacing_score"]) > float(a_full["binary_spacing_score"])
        and float(b_full["triplet_spacing_score"]) > float(b_full["binary_spacing_score"])
        and min(triplet_windows) >= 2
    ):
        return "triplet_spacing_reproduced", ["both_models_full_and_at_least_two_of_three_windows"]
    if (
        float(a_full["triplet_spacing_score"]) <= 0.1
        and float(b_full["triplet_spacing_score"]) <= 0.1
        and float(a_full["phase_entropy_0_concentrated_1_diffuse"]) <= 0.5
        and float(b_full["phase_entropy_0_concentrated_1_diffuse"]) <= 0.5
        and min(nontriplet_windows) >= 2
    ):
        return "concentrated_non_triplet_reproduced", ["both_models_full_and_at_least_two_of_three_windows"]
    return "stable_intermediate", ["passed_reliability_gate_but_did_not_meet_extreme_pattern_rules"]


def audit(blind_id: str) -> dict[str, object]:
    a_path = ROOT / f"blind20-separated/model-a/{blind_id}_(Drums)_kuielab_a_drums.wav"
    b_path = ROOT / f"blind20-separated/model-b/{blind_id}_(Drums)_kuielab_b_drums.wav"
    a, b = mono(a_path), mono(b_path)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    a_full, b_full = phase_features(a.astype(np.float32)), phase_features(b.astype(np.float32))
    a_windows, b_windows = windows(a), windows(b)
    category, reasons = classify(a_full, b_full, a_windows, b_windows)
    return {
        "blind_id": blind_id,
        "category": category,
        "reasons": reasons,
        "a_b_waveform_cosine": round(cosine(a[:, None], b[:, None]), 4),
        "a_b_scale_invariant_similarity_db_not_separation_quality": round(si_sdr(a[:, None], b[:, None]), 3),
        "model_a": {"full": a_full, "windows": a_windows},
        "model_b": {"full": b_full, "windows": b_windows},
    }


def main() -> None:
    manifest = json.loads((ROOT / "blind20-manifest.json").read_text())
    tracks = [audit(row["blind_id"]) for row in manifest["selected"]]
    counts = Counter(row["category"] for row in tracks)
    result = {
        "protocol": manifest["protocol"],
        "analysis_state": "blind IDs only; source paths and titles not used by this program",
        "task_boundary": "within-artist recurrence of estimated drum onset-spacing patterns in unknown-position 30-second previews",
        "metric_boundary": "The scale-invariant A/B waveform value is only model-to-model similarity, not source-separation SDR: real-track ground-truth stems do not exist",
        "precommitted_rules": {
            "reliability_gate": "both full beat confidence >=1.5, both three-window BPM series non-unstable, A/B full BPM pulse-family distance <=4%",
            "triplet": "both full triplet scores >=0.5 and exceed binary score; each model passes in >=2/3 windows",
            "concentrated_non_triplet": "both full triplet scores <=0.1 and entropy <=0.5; each model has >=2/3 windows <=0.1",
        },
        "category_counts": dict(counts),
        "tracks": tracks,
    }
    output = ROOT / "blind20-results-blinded.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"category_counts": dict(counts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
