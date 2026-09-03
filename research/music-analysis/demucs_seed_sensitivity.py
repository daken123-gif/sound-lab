#!/usr/bin/env python3
"""Measure whether frozen onset-spacing classifications survive Demucs seeds."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from collections import Counter
from pathlib import Path

import essentia

from demucs_blind20_audit import classify, mono, phase_features, windows


ROOT = Path(__file__).parent
DEFAULT_IDS = ("B06", "B09", "B10", "B14", "B16", "B17", "B19")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stems-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ids", nargs="+", default=list(DEFAULT_IDS))
    parser.add_argument("--seeds", nargs="+", type=int, default=list(range(5)))
    args = parser.parse_args()

    manifest = json.loads((ROOT / "blind20-manifest.json").read_text())
    mdx = json.loads((ROOT / "blind20-results-blinded.json").read_text())
    titles = json.loads((ROOT / "blind20-title-map.json").read_text())
    valid_ids = {row["blind_id"] for row in manifest["selected"]}
    mdx_by_id = {row["blind_id"]: row for row in mdx["tracks"]}
    title_by_id = {row["blind_id"]: row for row in titles["tracks"]}
    unknown = sorted(set(args.ids) - valid_ids)
    if unknown:
        raise SystemExit(f"unknown blind IDs: {', '.join(unknown)}")

    tracks = []
    for blind_id in args.ids:
        runs = []
        for seed in args.seeds:
            stem = args.stems_root / f"seed-{seed}" / f"{blind_id}-drums.wav"
            if not stem.exists():
                raise SystemExit(f"missing Demucs drum stem: {stem}")
            audio = mono(stem)
            full = phase_features(audio)
            window_rows = windows(audio)
            category, reasons = classify(full, window_rows)
            runs.append({
                "seed": seed,
                "stem_sha256": sha256(stem),
                "category": category,
                "reasons": reasons,
                "full": full,
                "windows": window_rows,
            })

        counts = Counter(run["category"] for run in runs)
        max_count = max(counts.values())
        majority = sorted(category for category, count in counts.items() if count == max_count)
        unanimous = len(counts) == 1
        mdx_category = mdx_by_id[blind_id]["category"]
        tracks.append({
            "blind_id": blind_id,
            "title": title_by_id[blind_id]["title"],
            "mdx_consensus_category": mdx_category,
            "category_counts": dict(sorted(counts.items())),
            "unanimous_across_seeds": unanimous,
            "majority_categories": majority,
            "majority_agrees_with_mdx": len(majority) == 1 and majority[0] == mdx_category,
            "runs": runs,
        })

    unanimous_count = sum(row["unanimous_across_seeds"] for row in tracks)
    result = {
        "protocol": manifest["protocol"],
        "experiment": "official Demucs seed sensitivity on predeclared disagreement/borderline panel",
        "panel_rationale": {
            "B09": "Billy Jack positive control under both MDX and seed-0 Demucs",
            "B06_B10_B14": "seed-0 Demucs positive while MDX consensus was stable intermediate",
            "B16_B17": "seed-0 Demucs stable intermediate while MDX consensus was rejected",
            "B19": "initial unseeded Demucs positive but seeded Demucs stable intermediate",
        },
        "separator": {
            "architecture": "Hybrid Transformer Demucs",
            "implementation": "demucs",
            "implementation_version": "4.0.1",
            "device": "Linux CPU",
            "model": "htdemucs",
            "shifts": 1,
            "seeds": args.seeds,
            "overlap": 0.25,
        },
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "essentia": getattr(essentia, "__version__", "unknown"),
        },
        "task_boundary": "seed sensitivity of separator output; feature extractor and thresholds are frozen",
        "metric_boundary": "no real-stem ground truth; categories measure recurrence, not separation SDR",
        "summary": {
            "tracks": len(tracks),
            "seeds_per_track": len(args.seeds),
            "separations": len(tracks) * len(args.seeds),
            "unanimous_tracks": unanimous_count,
            "non_unanimous_tracks": len(tracks) - unanimous_count,
        },
        "tracks": tracks,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["summary"], ensure_ascii=False))
    for row in tracks:
        print(row["blind_id"], row["category_counts"])


if __name__ == "__main__":
    main()
