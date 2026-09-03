#!/usr/bin/env python3
"""Robustness checks for DJ Shadow preview boundary and alignment hypotheses.

All results are bounded to Apple Music preview excerpts. Candidate changes are
signal-feature navigation aids, not semantic sections or full-track claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

from analyze_previews import decode as decode_calibrated
from calibrate_analyzer import SR as CALIBRATED_SR, periodicity_candidates
from compare_shadow_previews import HOP, SR, aligned_correlation, decode, features


STEM = "stem-long-stem-preview.m4a"
STEM_COPS = "stem-cops-robbers-preview.m4a"
NAPALM = "napalm-scatter-preview.m4a"
FEATURE_NAMES = [
    "rms_dbfs",
    "onsets_per_second",
    "band_20_150",
    "band_150_1000",
    "band_1000_6000",
    "band_6000_nyquist",
]
SOURCE_HASHES = {
    STEM: "12f10578146558fd2e15d8342314b8f1a155481522ec514e40887c77d00264a7",
    STEM_COPS: "317551ae1ad70813f818fbe1ae7c7a4e101cf36c3ef1980e88444f916d3f9b29",
    NAPALM: "ba0146f68a8c7b607099ea9fd14e357c5adadcee40cd4caff839f7dad985f0d6",
}


def window_vector(x: np.ndarray, start_s: float, window_s: float) -> np.ndarray:
    part = x[int(start_s * SR):int((start_s + window_s) * SR)]
    f = features(part)
    distance = max(1, int(round(0.09 * SR / HOP)))
    peaks, _ = find_peaks(
        f["flux"], height=1.0, distance=distance, prominence=0.35
    )
    rms_db = 20.0 * np.log10(np.sqrt(np.mean(part * part)) + 1e-12)
    return np.asarray([rms_db, len(peaks) / window_s, *f["band_ratio"]])


def novelty_series(
    x: np.ndarray, window_s: float, hop_s: float = 0.25
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    duration_s = len(x) / SR
    starts = np.arange(0.0, duration_s - window_s - 1e-9, hop_s)
    values = np.asarray([window_vector(x, float(t), window_s) for t in starts])
    z = (values - values.mean(axis=0)) / (values.std(axis=0) + 1e-12)
    delta = np.diff(z, axis=0)
    return starts[1:], np.linalg.norm(delta, axis=1), delta


def candidate_robustness(
    x: np.ndarray, reference_s: float, window_lengths: list[float]
) -> dict[str, object]:
    settings = []
    for window_s in window_lengths:
        times, novelty, delta = novelty_series(x, window_s)
        peaks, _ = find_peaks(novelty, distance=max(1, int(round(1.0 / 0.25))))
        local = peaks[np.abs(times[peaks] - reference_s) <= 1.0]
        if len(local):
            index = int(local[np.argmax(novelty[local])])
        else:
            index = int(np.argmin(np.abs(times - reference_s)))
        rank = int(1 + np.sum(novelty > novelty[index]))
        percentile = float(100.0 * np.mean(novelty <= novelty[index]))
        squared = delta[index] ** 2
        shares = squared / (squared.sum() + 1e-12)
        settings.append({
            "window_s": window_s,
            "nearest_local_peak_s": round(float(times[index]), 2),
            "distance_from_reference_s": round(float(times[index] - reference_s), 2),
            "novelty": round(float(novelty[index]), 3),
            "global_rank_among_hops": rank,
            "percentile_among_hops": round(percentile, 1),
            "top_contributors": [
                {"feature": FEATURE_NAMES[i], "squared_distance_share": round(float(shares[i]), 3)}
                for i in np.argsort(shares)[::-1][:3]
            ],
        })
    return {
        "reference_s": reference_s,
        "search_radius_s": 1.0,
        "settings": settings,
        "median_peak_s": round(float(np.median([s["nearest_local_peak_s"] for s in settings])), 2),
        "peak_time_range_s": [
            min(s["nearest_local_peak_s"] for s in settings),
            max(s["nearest_local_peak_s"] for s in settings),
        ],
        "settings_at_or_above_90th_percentile": sum(
            s["percentile_among_hops"] >= 90.0 for s in settings
        ),
        "settings_tested": len(settings),
    }


def segment_alignment(a: np.ndarray, b: np.ndarray) -> list[dict[str, object]]:
    rows = []
    for start_s, end_s in [(0.0, 10.0), (10.0, 20.0), (20.0, 29.5)]:
        aa = a[int(start_s * SR):int(end_s * SR)]
        bb = b[int(start_s * SR):int(end_s * SR)]
        af, bf = features(aa), features(bb)
        rows.append({
            "range_s": [start_s, end_s],
            "onset_envelope": aligned_correlation(af["flux"], bf["flux"]),
            "rms_envelope": aligned_correlation(af["rms"], bf["rms"]),
        })
    return rows


def onset_event_match(a: np.ndarray, b: np.ndarray, lag_s: float) -> dict[str, object]:
    def event_times(x: np.ndarray) -> np.ndarray:
        env = features(x)["flux"]
        distance = max(1, int(round(0.09 * SR / HOP)))
        peaks, _ = find_peaks(env, height=1.0, distance=distance, prominence=0.35)
        return peaks * HOP / SR

    ta, tb = event_times(a), event_times(b)
    shifted_a = ta + lag_s
    distances = np.asarray([
        np.min(np.abs(tb - value)) if len(tb) else np.inf for value in shifted_a
    ])
    return {
        "tested_lag_s": lag_s,
        "events_a": len(ta),
        "events_b": len(tb),
        "a_events_matched_within_50ms": int(np.sum(distances <= 0.05)),
        "a_events_matched_within_100ms": int(np.sum(distances <= 0.10)),
        "match_rate_within_50ms": round(float(np.mean(distances <= 0.05)), 3),
        "match_rate_within_100ms": round(float(np.mean(distances <= 0.10)), 3),
        "median_nearest_event_distance_s": round(float(np.median(distances)), 4),
    }


def napalm_periodicity_stability(path: Path) -> dict[str, object]:
    x = decode_calibrated(path)
    rows = []
    for window_s in [6.0, 8.0, 10.0, 12.0, 15.0]:
        hop_s = window_s / 2.0
        starts = np.arange(0.0, len(x) / CALIBRATED_SR - window_s + 1e-9, hop_s)
        for start_s in starts:
            part = x[
                int(start_s * CALIBRATED_SR):int((start_s + window_s) * CALIBRATED_SR)
            ]
            candidates = periodicity_candidates(part, CALIBRATED_SR)[:8]
            rows.append({
                "window_s": window_s,
                "range_s": [round(float(start_s), 2), round(float(start_s + window_s), 2)],
                "candidates_bpm": [round(float(v), 2) for v in candidates],
                "has_70_75_family": any(70.0 <= v <= 75.0 for v in candidates),
                "has_140_150_family": any(140.0 <= v <= 150.0 for v in candidates),
            })
    return {
        "windows": rows,
        "window_count": len(rows),
        "70_75_family_support": round(float(np.mean([r["has_70_75_family"] for r in rows])), 3),
        "140_150_family_support": round(float(np.mean([r["has_140_150_family"] for r in rows])), 3),
        "either_family_support": round(float(np.mean([
            r["has_70_75_family"] or r["has_140_150_family"] for r in rows
        ])), 3),
    }


def main() -> None:
    stem = decode(Path(STEM))
    stem_cops = decode(Path(STEM_COPS))
    napalm = decode(Path(NAPALM))
    windows = [1.0, 1.5, 2.0, 3.0, 4.0]
    stem_segments = segment_alignment(stem, stem_cops)
    lag_values = [
        row["onset_envelope"]["lag_s"] for row in stem_segments
    ]
    report = {
        "analysis_date_utc": "2026-09-03",
        "source_previews_sha256": SOURCE_HASHES,
        "method": {
            "boundary_window_lengths_s": windows,
            "boundary_hop_s": 0.25,
            "candidate_search_radius_s": 1.0,
            "feature_contribution_definition": "squared share of standardized adjacent-window delta",
        },
        "candidate_robustness": {
            "stem_reference_3_5s": candidate_robustness(stem, 3.5, windows),
            "napalm_reference_4_5s": candidate_robustness(napalm, 4.5, windows),
        },
        "stem_album_vs_cops_alignment": {
            "segment_results": stem_segments,
            "segment_onset_lag_range_s": [min(lag_values), max(lag_values)],
            "whole_preview_event_match_at_previous_best_lag": onset_event_match(stem, stem_cops, 0.7314),
            "interpretation_guardrail": "A stable nonzero feature lag may indicate excerpt placement or an edit; codec delay requires fine waveform evidence and is not established here.",
        },
        "napalm_periodicity_window_robustness": napalm_periodicity_stability(Path(NAPALM)),
        "limits": [
            "all analysis is limited to approximately 30-second Apple Music previews",
            "preview source positions are unknown",
            "feature novelty is not a semantic scene-boundary detector",
            "periodicity candidates are not equivalent to a human beat judgment",
            "no listening judgment or full-track analysis is claimed",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
