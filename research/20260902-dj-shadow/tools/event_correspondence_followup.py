#!/usr/bin/env python3
"""One-to-one onset-event correspondence for two DJ Shadow previews.

This does not identify samples or prove edition lineage. It tests whether the
previous whole-preview feature lag behaves like a constant event-sequence lag.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks, stft

from compare_shadow_previews import HOP, NFFT, SR, decode


ALBUM = "stem-long-stem-preview.m4a"
COPS = "stem-cops-robbers-preview.m4a"
PREVIOUS_FEATURE_LAG_S = 0.7314
TOLERANCE_S = 0.05
SOURCE_HASHES = {
    ALBUM: "12f10578146558fd2e15d8342314b8f1a155481522ec514e40887c77d00264a7",
    COPS: "317551ae1ad70813f818fbe1ae7c7a4e101cf36c3ef1980e88444f916d3f9b29",
}


@dataclass
class Events:
    times: np.ndarray
    descriptors: np.ndarray


def extract_events(x: np.ndarray) -> Events:
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

    power = magnitude ** 2
    bands = []
    for lo, hi in [(20, 150), (150, 1000), (1000, 6000), (6000, SR / 2)]:
        mask = (frequencies >= lo) & (frequencies < hi)
        bands.append(power[mask].sum(axis=0))
    band_ratio = np.vstack(bands)
    band_ratio /= band_ratio.sum(axis=0, keepdims=True) + 1e-12
    centroid = (
        (frequencies[:, None] * magnitude).sum(axis=0)
        / (magnitude.sum(axis=0) + 1e-12)
    ) / (SR / 2)
    rms = np.sqrt(np.mean(magnitude * magnitude, axis=0))
    rms /= np.percentile(rms, 95) + 1e-12

    frame_indices = np.minimum(peaks + 1, magnitude.shape[1] - 1)
    descriptors = np.column_stack([
        band_ratio[:, frame_indices].T,
        centroid[frame_indices],
        rms[frame_indices],
    ])
    descriptors /= np.linalg.norm(descriptors, axis=1, keepdims=True) + 1e-12
    return Events(frame_times[frame_indices], descriptors)


def better(a: tuple[int, float], b: tuple[int, float]) -> bool:
    """True when score a is lexicographically better: more matches, less error."""
    return a[0] > b[0] or (a[0] == b[0] and a[1] < b[1])


def one_to_one_match(
    a: np.ndarray, b: np.ndarray, lag_s: float, tolerance_s: float
) -> list[tuple[int, int, float]]:
    shifted = a + lag_s
    n, m = len(a), len(b)
    score = [[(0, 0.0) for _ in range(m + 1)] for _ in range(n + 1)]
    action = np.zeros((n + 1, m + 1), dtype=np.int8)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            best, act = score[i - 1][j], 1
            if better(score[i][j - 1], best):
                best, act = score[i][j - 1], 2
            error = abs(float(shifted[i - 1] - b[j - 1]))
            if error <= tolerance_s:
                prev = score[i - 1][j - 1]
                candidate = (prev[0] + 1, prev[1] + error)
                if better(candidate, best):
                    best, act = candidate, 3
            score[i][j], action[i, j] = best, act
    pairs: list[tuple[int, int, float]] = []
    i, j = n, m
    while i and j:
        act = int(action[i, j])
        if act == 3:
            error = float(shifted[i - 1] - b[j - 1])
            pairs.append((i - 1, j - 1, error))
            i -= 1
            j -= 1
        elif act == 1:
            i -= 1
        else:
            j -= 1
    return list(reversed(pairs))


def summarize_match(a: Events, b: Events, lag_s: float) -> dict[str, object]:
    pairs = one_to_one_match(a.times, b.times, lag_s, TOLERANCE_S)
    errors = np.asarray([pair[2] for pair in pairs])
    similarities = np.asarray([
        float(np.dot(a.descriptors[i], b.descriptors[j])) for i, j, _ in pairs
    ])
    runs: list[list[tuple[int, int, float]]] = []
    current: list[tuple[int, int, float]] = []
    previous: tuple[int, int] | None = None
    for pair in pairs:
        i, j, _ = pair
        if previous is not None and i == previous[0] + 1 and j == previous[1] + 1:
            current.append(pair)
        else:
            if current:
                runs.append(current)
            current = [pair]
        previous = (i, j)
    if current:
        runs.append(current)
    longest = max(runs, key=len, default=[])
    longest_region = None
    if longest:
        ai = [pair[0] for pair in longest]
        bj = [pair[1] for pair in longest]
        run_residuals = [abs(pair[2]) for pair in longest]
        run_similarities = [
            float(np.dot(a.descriptors[i], b.descriptors[j])) for i, j, _ in longest
        ]
        longest_region = {
            "album_event_time_range_s": [round(float(a.times[ai[0]]), 4), round(float(a.times[ai[-1]]), 4)],
            "cops_event_time_range_s": [round(float(b.times[bj[0]]), 4), round(float(b.times[bj[-1]]), 4)],
            "album_span_s": round(float(a.times[ai[-1]] - a.times[ai[0]]), 4),
            "median_absolute_residual_s": round(float(np.median(run_residuals)), 4),
            "median_descriptor_cosine": round(float(np.median(run_similarities)), 4),
        }
    return {
        "lag_s": round(lag_s, 4),
        "matched_pairs": len(pairs),
        "album_event_coverage": round(len(pairs) / max(1, len(a.times)), 3),
        "cops_event_coverage": round(len(pairs) / max(1, len(b.times)), 3),
        "median_absolute_residual_s": round(float(np.median(np.abs(errors))), 4) if len(errors) else None,
        "p90_absolute_residual_s": round(float(np.percentile(np.abs(errors), 90)), 4) if len(errors) else None,
        "median_descriptor_cosine": round(float(np.median(similarities)), 4) if len(similarities) else None,
        "longest_consecutive_index_run": len(longest),
        "longest_consecutive_run_region": longest_region,
    }


def scan_lags(a: Events, b: Events) -> dict[str, object]:
    rows = []
    for lag_s in np.arange(-2.0, 2.0001, 0.01):
        pairs = one_to_one_match(a.times, b.times, float(lag_s), TOLERANCE_S)
        residual = sum(abs(pair[2]) for pair in pairs)
        rows.append((len(pairs), residual, float(lag_s)))
    rows.sort(key=lambda item: (-item[0], item[1]))
    best_count = rows[0][0]
    tied = [row for row in rows if row[0] == best_count]
    previous = one_to_one_match(
        a.times, b.times, PREVIOUS_FEATURE_LAG_S, TOLERANCE_S
    )
    previous_count = len(previous)
    count_percentile = 100.0 * np.mean([row[0] <= previous_count for row in rows])
    return {
        "grid_s": [-2.0, 2.0, 0.01],
        "tolerance_s": TOLERANCE_S,
        "maximum_matched_pairs": best_count,
        "best_lag_s": round(rows[0][2], 4),
        "equal_maximum_lag_span_s": [
            round(min(row[2] for row in tied), 4),
            round(max(row[2] for row in tied), 4),
        ],
        "equal_maximum_lags_s": [round(row[2], 4) for row in tied],
        "previous_lag_matched_pairs": previous_count,
        "previous_lag_count_percentile_across_grid": round(float(count_percentile), 1),
        "top_five_lags": [
            {"lag_s": round(row[2], 4), "matched_pairs": row[0], "total_absolute_residual_s": round(row[1], 4)}
            for row in rows[:5]
        ],
    }


def local_blocks(a: Events, b: Events) -> list[dict[str, object]]:
    rows = []
    for start_s in np.arange(0.0, 25.0, 5.0):
        end_s = start_s + 5.0
        mask = (a.times >= start_s) & (a.times < end_s)
        local_a = Events(a.times[mask], a.descriptors[mask])
        scan = scan_lags(local_a, b)
        rows.append({
            "album_range_s": [float(start_s), float(end_s)],
            "album_events": len(local_a.times),
            "best_lag_s": scan["best_lag_s"],
            "equal_maximum_lag_span_s": scan["equal_maximum_lag_span_s"],
            "maximum_matched_pairs": scan["maximum_matched_pairs"],
            "coverage_at_best_lag": round(scan["maximum_matched_pairs"] / max(1, len(local_a.times)), 3),
        })
    return rows


def main() -> None:
    album = extract_events(decode(Path(ALBUM)))
    cops = extract_events(decode(Path(COPS)))
    grid_scan = scan_lags(album, cops)
    report = {
        "analysis_date_utc": "2026-09-04",
        "source_previews_sha256": SOURCE_HASHES,
        "event_extractor": {
            "sample_rate": SR,
            "stft_nfft": NFFT,
            "hop_samples": HOP,
            "peak_minimum_distance_s": 0.09,
            "match_tolerance_s": TOLERANCE_S,
            "event_descriptor": "four band-energy ratios plus normalized centroid and RMS",
        },
        "event_counts": {"album": len(album.times), "cops": len(cops.times)},
        "previous_feature_lag_one_to_one": summarize_match(
            album, cops, PREVIOUS_FEATURE_LAG_S
        ),
        "lag_grid_scan": grid_scan,
        "best_grid_lag_one_to_one": summarize_match(
            album, cops, float(grid_scan["best_lag_s"])
        ),
        "five_second_local_lag_scans": local_blocks(album, cops),
        "limits": [
            "analysis is limited to two approximately 30-second Apple Music previews",
            "preview source positions are unknown",
            "dense or periodic event trains can produce high one-to-one proximity by chance",
            "descriptor cosine is coarse spectral-event similarity, not sample identity",
            "the analysis does not establish codec delay, edit lineage, or a semantic scene boundary",
            "no listening judgment is claimed",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
