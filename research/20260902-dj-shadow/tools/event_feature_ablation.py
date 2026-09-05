#!/usr/bin/env python3
"""Feature-ablation controls for the DJ Shadow 9-event correspondence."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks, stft

from compare_shadow_previews import HOP, NFFT, SR, decode
from event_correspondence_followup import ALBUM, COPS, SOURCE_HASHES


ALBUM_START_INDEX = 36
COPS_START_INDEX = 15
LENGTH = 9

BAND_SETS = {
    "broad4": [20, 150, 1000, 6000, SR / 2],
    "medium8": [20, 80, 150, 300, 600, 1000, 3000, 6000, SR / 2],
    "fine12": [20, 50, 100, 150, 250, 400, 650, 1000, 1600, 2500, 4000, 6500, SR / 2],
}

CONFIGS = [
    ("broad4_centroid_rms", "broad4", True, True),
    ("broad4_only", "broad4", False, False),
    ("broad4_centroid", "broad4", True, False),
    ("broad4_rms", "broad4", False, True),
    ("medium8_centroid_rms", "medium8", True, True),
    ("medium8_only", "medium8", False, False),
    ("medium8_centroid", "medium8", True, False),
    ("medium8_rms", "medium8", False, True),
    ("fine12_centroid_rms", "fine12", True, True),
    ("fine12_only", "fine12", False, False),
    ("fine12_centroid", "fine12", True, False),
    ("fine12_rms", "fine12", False, True),
    ("centroid_rms_only", None, True, True),
]


def event_frames(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    frequencies, frame_times, spectrum = stft(
        x,
        fs=SR,
        window="hann",
        nperseg=NFFT,
        noverlap=NFFT - HOP,
        boundary=None,
        padded=False,
    )
    magnitude = np.abs(spectrum)
    log_magnitude = np.log1p(10.0 * magnitude)
    flux = np.maximum(0.0, np.diff(log_magnitude, axis=1)).mean(axis=0)
    flux = (flux - np.median(flux)) / (np.std(flux) + 1e-12)
    flux = np.maximum(0.0, flux)
    distance = max(1, int(round(0.09 * SR / HOP)))
    peaks, _ = find_peaks(flux, height=1.0, distance=distance, prominence=0.35)
    indices = np.minimum(peaks + 1, magnitude.shape[1] - 1)
    return frequencies, frame_times[indices], magnitude, indices


def descriptors(
    frequencies: np.ndarray,
    magnitude: np.ndarray,
    indices: np.ndarray,
    band_edges: list[float] | None,
    include_centroid: bool,
    include_rms: bool,
) -> np.ndarray:
    columns: list[np.ndarray] = []
    if band_edges is not None:
        power = magnitude ** 2
        bands = []
        for lo, hi in zip(band_edges[:-1], band_edges[1:]):
            mask = (frequencies >= lo) & (frequencies < hi)
            bands.append(power[mask].sum(axis=0))
        ratio = np.vstack(bands)
        ratio /= ratio.sum(axis=0, keepdims=True) + 1e-12
        columns.append(ratio[:, indices].T)
    if include_centroid:
        centroid = (
            (frequencies[:, None] * magnitude).sum(axis=0)
            / (magnitude.sum(axis=0) + 1e-12)
        ) / (SR / 2)
        columns.append(centroid[indices, None])
    if include_rms:
        rms = np.sqrt(np.mean(magnitude * magnitude, axis=0))
        rms /= np.percentile(rms, 95) + 1e-12
        columns.append(rms[indices, None])
    result = np.column_stack(columns)
    result /= np.linalg.norm(result, axis=1, keepdims=True) + 1e-12
    return result


def scalar_descriptors(
    frequencies: np.ndarray,
    magnitude: np.ndarray,
    indices: np.ndarray,
    kind: str,
) -> np.ndarray:
    if kind == "centroid":
        values = (
            (frequencies[:, None] * magnitude).sum(axis=0)
            / (magnitude.sum(axis=0) + 1e-12)
        ) / (SR / 2)
    elif kind == "rms":
        values = np.sqrt(np.mean(magnitude * magnitude, axis=0))
        values /= np.percentile(values, 95) + 1e-12
    else:
        raise ValueError(kind)
    return values[indices, None]


def trajectory_cosine(a: np.ndarray, b: np.ndarray) -> float:
    joined = np.vstack([a, b])
    scale = joined.std(axis=0) + 1e-12
    aa = (a - a.mean(axis=0)) / scale
    bb = (b - b.mean(axis=0)) / scale
    av, bv = aa.ravel(), bb.ravel()
    return float(np.dot(av, bv) / (np.linalg.norm(av) * np.linalg.norm(bv) + 1e-12))


def score_config(
    album: np.ndarray,
    cops: np.ndarray,
    name: str,
    dimensions: int,
) -> dict[str, object]:
    candidate = round(
        trajectory_cosine(
            album[ALBUM_START_INDEX:ALBUM_START_INDEX + LENGTH],
            cops[COPS_START_INDEX:COPS_START_INDEX + LENGTH],
        ),
        4,
    )
    controls = [
        round(trajectory_cosine(album[ai:ai + LENGTH], cops[bj:bj + LENGTH]), 4)
        for ai in range(len(album) - LENGTH + 1)
        for bj in range(len(cops) - LENGTH + 1)
    ]
    better = sum(value > candidate for value in controls)
    n = len(controls)
    return {
        "config": name,
        "dimensions": dimensions,
        "candidate_trajectory_cosine": candidate,
        "rank_higher_is_better": better + 1,
        "comparison_pairs": n,
        "percentile_better_than": round(100.0 * (n - better - 1) / n, 2),
        "control_distribution": {
            "median": round(float(np.median(controls)), 4),
            "p95": round(float(np.percentile(controls, 95)), 4),
            "p99": round(float(np.percentile(controls, 99)), 4),
        },
    }


def main() -> None:
    album_audio = decode(Path(ALBUM))
    cops_audio = decode(Path(COPS))
    af, at, am, ai = event_frames(album_audio)
    cf, ct, cm, ci = event_frames(cops_audio)
    results = []
    for name, band_name, use_centroid, use_rms in CONFIGS:
        edges = BAND_SETS[band_name] if band_name is not None else None
        ad = descriptors(af, am, ai, edges, use_centroid, use_rms)
        cd = descriptors(cf, cm, ci, edges, use_centroid, use_rms)
        results.append(score_config(ad, cd, name, ad.shape[1]))
    post_hoc_scalar_results = []
    for kind in ["centroid", "rms"]:
        ad = scalar_descriptors(af, am, ai, kind)
        cd = scalar_descriptors(cf, cm, ci, kind)
        post_hoc_scalar_results.append(
            score_config(ad, cd, f"{kind}_only", 1)
        )
    percentiles = [row["percentile_better_than"] for row in results]
    report = {
        "analysis_date_utc": "2026-09-05",
        "source_previews_sha256": SOURCE_HASHES,
        "fixed_candidate": {
            "album_event_indices": [ALBUM_START_INDEX, ALBUM_START_INDEX + LENGTH - 1],
            "cops_event_indices": [COPS_START_INDEX, COPS_START_INDEX + LENGTH - 1],
            "album_time_range_s": [round(float(at[ALBUM_START_INDEX]), 4), round(float(at[ALBUM_START_INDEX + LENGTH - 1]), 4)],
            "cops_time_range_s": [round(float(ct[COPS_START_INDEX]), 4), round(float(ct[COPS_START_INDEX + LENGTH - 1]), 4)],
            "length_events": LENGTH,
        },
        "feature_configurations": results,
        "post_hoc_scalar_diagnostics": {
            "status": "added after the 13-configuration result showed centroid-plus-RMS dominance",
            "results": post_hoc_scalar_results,
        },
        "robustness_summary": {
            "configurations_tested": len(results),
            "configurations_at_or_above_95th_percentile": sum(value >= 95.0 for value in percentiles),
            "configurations_at_or_above_90th_percentile": sum(value >= 90.0 for value in percentiles),
            "minimum_percentile": min(percentiles),
            "maximum_percentile": max(percentiles),
        },
        "limits": [
            "the candidate indices were fixed from the earlier analysis, but the same two previews supply all controls",
            "the core 13 feature configurations were specified before inspecting their results",
            "centroid-only and RMS-only diagnostics were added after inspecting the core result and are explicitly post hoc",
            "broad-band descriptors cannot establish sample identity or production lineage",
            "ranks are descriptive internal controls, not confirmatory p-values",
            "no listening judgment or full-track inference is claimed",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
