#!/usr/bin/env python3
"""Apply the frozen onset-spacing rules to independent Demucs drum estimates."""

from __future__ import annotations

import argparse
import json
import platform
from collections import Counter
from pathlib import Path

import essentia
import essentia.standard as es
import numpy as np

from essentia_compare import SR
from phase_analysis import phase_features
from reliability_audit import classify_bpm


ROOT = Path(__file__).parent


def mono(path: Path) -> np.ndarray:
    return es.MonoLoader(filename=str(path), sampleRate=SR)().astype(np.float32)


def windows(audio: np.ndarray) -> list[dict[str, object]]:
    rows = []
    for start_s in (0, 10, 20):
        start = start_s * SR
        stop = min(len(audio), (start_s + 10) * SR)
        rows.append({"seconds": [start_s, round(stop / SR, 3)], **phase_features(audio[start:stop])})
    return rows


def classify(full: dict, window_rows: list[dict]) -> tuple[str, list[str]]:
    reasons = []
    stability = classify_bpm([float(row["bpm_candidate"]) for row in window_rows])[0]
    if float(full["beat_confidence"]) < 1.5:
        reasons.append("full_excerpt_low_beat_confidence")
    if stability == "unstable":
        reasons.append("window_bpm_unstable")
    if reasons:
        return "rejected", reasons

    triplet_windows = sum(
        float(row["beat_confidence"]) >= 1.5
        and float(row["triplet_spacing_score"]) >= 0.5
        and float(row["triplet_spacing_score"]) > float(row["binary_spacing_score"])
        for row in window_rows
    )
    nontriplet_windows = sum(
        float(row["beat_confidence"]) >= 1.5 and float(row["triplet_spacing_score"]) <= 0.1
        for row in window_rows
    )
    if (
        float(full["triplet_spacing_score"]) >= 0.5
        and float(full["triplet_spacing_score"]) > float(full["binary_spacing_score"])
        and triplet_windows >= 2
    ):
        return "triplet_spacing_reproduced", ["full_and_at_least_two_of_three_windows"]
    if (
        float(full["triplet_spacing_score"]) <= 0.1
        and float(full["phase_entropy_0_concentrated_1_diffuse"]) <= 0.5
        and nontriplet_windows >= 2
    ):
        return "concentrated_non_triplet_reproduced", ["full_and_at_least_two_of_three_windows"]
    return "stable_intermediate", ["passed_reliability_gate_but_did_not_meet_extreme_pattern_rules"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stems", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads((ROOT / "blind20-manifest.json").read_text())
    mdx = json.loads((ROOT / "blind20-results-blinded.json").read_text())
    mdx_by_id = {row["blind_id"]: row for row in mdx["tracks"]}
    tracks = []
    for selected in manifest["selected"]:
        blind_id = selected["blind_id"]
        stem = args.stems / f"{blind_id}-drums.wav"
        if not stem.exists():
            raise SystemExit(f"missing Demucs drum stem: {stem}")
        audio = mono(stem)
        full = phase_features(audio)
        window_rows = windows(audio)
        category, reasons = classify(full, window_rows)
        mdx_category = mdx_by_id[blind_id]["category"]
        tracks.append({
            "blind_id": blind_id,
            "demucs_category": category,
            "mdx_consensus_category": mdx_category,
            "exact_category_agreement": category == mdx_category,
            "reasons": reasons,
            "full": full,
            "windows": window_rows,
        })

    categories = Counter(row["demucs_category"] for row in tracks)
    exact = sum(row["exact_category_agreement"] for row in tracks)
    result = {
        "protocol": manifest["protocol"],
        "separator": {
            "architecture": "Hybrid Transformer Demucs",
            "implementation": "demucs-mlx",
            "model": "htdemucs",
            "shifts": 1,
            "seed": 0,
            "overlap": 0.25,
        },
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "essentia": getattr(essentia, "__version__", "unknown"),
        },
        "task_boundary": "independent separator architecture check; feature extractor and frozen thresholds remain shared",
        "metric_boundary": "no ground-truth real stems; this tests recurrence of derived onset-spacing categories, not separation SDR",
        "category_counts": dict(categories),
        "exact_category_agreement_with_mdx": {"count": exact, "total": len(tracks)},
        "tracks": tracks,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "category_counts": result["category_counts"],
        "exact_category_agreement_with_mdx": result["exact_category_agreement_with_mdx"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

