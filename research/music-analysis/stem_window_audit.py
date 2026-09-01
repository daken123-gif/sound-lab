#!/usr/bin/env python3
"""Windowed audit of derived drum/bass stems from the two Curtis previews."""

from __future__ import annotations

import json
from pathlib import Path

import essentia.standard as es
import numpy as np

from essentia_compare import SR
from phase_analysis import phase_features


ROOT = Path(__file__).parent
TRACKS = {
    "Billy Jack": {
        "mixture": ROOT.parent / "quota-probe-5/01-billy-jack.m4a",
        "drums": ROOT / "separated/billy-drums/01-billy-jack_(Drums)_kuielab_b_drums.wav",
        "no_drums": ROOT / "separated/billy-drums/01-billy-jack_(No Drums)_kuielab_b_drums.wav",
        "bass": ROOT / "separated/billy-bass/01-billy-jack_(Bass)_kuielab_b_bass.wav",
        "no_bass": ROOT / "separated/billy-bass/01-billy-jack_(No Bass)_kuielab_b_bass.wav",
    },
    "Sweet Exorcist": {
        "mixture": ROOT.parent / "quota-probe-100-add80/026-43465733.m4a",
        "drums": ROOT / "separated/sweet-drums/026-43465733_(Drums)_kuielab_b_drums.wav",
        "no_drums": ROOT / "separated/sweet-drums/026-43465733_(No Drums)_kuielab_b_drums.wav",
        "bass": ROOT / "separated/sweet-bass/026-43465733_(Bass)_kuielab_b_bass.wav",
        "no_bass": ROOT / "separated/sweet-bass/026-43465733_(No Bass)_kuielab_b_bass.wav",
    },
}


def mono(path: Path) -> np.ndarray:
    return es.MonoLoader(filename=str(path), sampleRate=SR)().astype(np.float64)


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x))))


def stem_audit(paths: dict[str, Path], stem: str) -> dict[str, object]:
    target_m = mono(paths[stem])
    complement_m = mono(paths[f"no_{stem}"])
    mix_m = mono(paths["mixture"])
    n = min(len(target_m), len(complement_m), len(mix_m))
    residual = mix_m[:n] - target_m[:n] - complement_m[:n]
    full = phase_features(target_m[:n].astype(np.float32))
    windows = []
    for start_s in (0, 10, 20):
        start = start_s * SR
        stop = min(n, (start_s + 10) * SR)
        if stop - start >= 8 * SR:
            windows.append({"seconds": [start_s, round(stop / SR, 3)], **phase_features(target_m[start:stop].astype(np.float32))})
    return {
        "derived_stem": stem,
        "rms_ratio_to_mixture": round(rms(target_m[:n]) / max(rms(mix_m[:n]), 1e-12), 4),
        "reconstruction_residual_rms": round(rms(residual), 7),
        "full_excerpt": full,
        "windows": windows,
    }


def main() -> None:
    result = {
        title: [stem_audit(paths, "drums"), stem_audit(paths, "bass")]
        for title, paths in TRACKS.items()
    }
    result["scope"] = {
        "source_status": "derived estimates, not multitracks",
        "acceptance_rule": "interpret phase features only when beat confidence is >= 1.5 and window behavior is not contradictory",
    }
    output = ROOT / "stem-window-results.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output.read_text(), end="")


if __name__ == "__main__":
    main()
