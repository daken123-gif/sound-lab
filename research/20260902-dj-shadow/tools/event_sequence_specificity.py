#!/usr/bin/env python3
"""Test whether the 9-event Stem correspondence is specific beyond periodicity."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from compare_shadow_previews import decode
from event_correspondence_followup import (
    ALBUM,
    COPS,
    SOURCE_HASHES,
    TOLERANCE_S,
    Events,
    extract_events,
    one_to_one_match,
)


CANDIDATE_LAG_S = 1.31


def consecutive_runs(pairs: list[tuple[int, int, float]]) -> list[list[tuple[int, int, float]]]:
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
    return runs


def trajectory_cosine(a: np.ndarray, b: np.ndarray) -> float:
    joined = np.vstack([a, b])
    scale = joined.std(axis=0) + 1e-12
    aa = (a - a.mean(axis=0)) / scale
    bb = (b - b.mean(axis=0)) / scale
    av, bv = aa.ravel(), bb.ravel()
    return float(np.dot(av, bv) / (np.linalg.norm(av) * np.linalg.norm(bv) + 1e-12))


def metrics(a: Events, b: Events, ai: int, bj: int, length: int) -> dict[str, object]:
    at = a.times[ai:ai + length]
    bt = b.times[bj:bj + length]
    ad = a.descriptors[ai:ai + length]
    bd = b.descriptors[bj:bj + length]
    lag = float(np.median(bt - at))
    residual = at + lag - bt
    a_ioi, b_ioi = np.diff(at), np.diff(bt)
    event_cosines = np.sum(ad * bd, axis=1)
    cross = ad @ bd.T
    off_diagonal = cross[~np.eye(length, dtype=bool)]
    return {
        "album_start_index": ai,
        "cops_start_index": bj,
        "length_events": length,
        "album_time_range_s": [round(float(at[0]), 4), round(float(at[-1]), 4)],
        "cops_time_range_s": [round(float(bt[0]), 4), round(float(bt[-1]), 4)],
        "median_lag_s": round(lag, 4),
        "timing_residual_rms_s": round(float(np.sqrt(np.mean(residual ** 2))), 6),
        "timing_residual_max_abs_s": round(float(np.max(np.abs(residual))), 6),
        "ioi_mae_s": round(float(np.mean(np.abs(a_ioi - b_ioi))), 6),
        "ioi_correlation": round(float(np.corrcoef(a_ioi, b_ioi)[0, 1]), 4),
        "eventwise_descriptor_cosine_median": round(float(np.median(event_cosines)), 4),
        "descriptor_trajectory_cosine": round(trajectory_cosine(ad, bd), 4),
        "descriptor_diagonal_advantage": round(float(np.mean(event_cosines) - np.mean(off_diagonal)), 4),
    }


def rank_against_all(candidate: dict[str, object], all_rows: list[dict[str, object]]) -> dict[str, object]:
    n = len(all_rows)
    timing = float(candidate["timing_residual_rms_s"])
    trajectory = float(candidate["descriptor_trajectory_cosine"])
    advantage = float(candidate["descriptor_diagonal_advantage"])
    timing_better = sum(float(row["timing_residual_rms_s"]) < timing for row in all_rows)
    trajectory_better = sum(float(row["descriptor_trajectory_cosine"]) > trajectory for row in all_rows)
    advantage_better = sum(float(row["descriptor_diagonal_advantage"]) > advantage for row in all_rows)
    joint_dominators = sum(
        float(row["timing_residual_rms_s"]) <= timing
        and float(row["descriptor_trajectory_cosine"]) >= trajectory
        and (
            float(row["timing_residual_rms_s"]) < timing
            or float(row["descriptor_trajectory_cosine"]) > trajectory
        )
        for row in all_rows
    )
    return {
        "comparison_pairs": n,
        "timing_rms_rank_lower_is_better": timing_better + 1,
        "timing_rms_percentile_better_than": round(100.0 * (n - timing_better - 1) / n, 2),
        "descriptor_trajectory_rank_higher_is_better": trajectory_better + 1,
        "descriptor_trajectory_percentile_better_than": round(100.0 * (n - trajectory_better - 1) / n, 2),
        "descriptor_diagonal_advantage_rank_higher_is_better": advantage_better + 1,
        "descriptor_diagonal_advantage_percentile_better_than": round(100.0 * (n - advantage_better - 1) / n, 2),
        "pairs_jointly_dominating_candidate_on_timing_and_trajectory": joint_dominators,
        "timing_rms_distribution_s": {
            "p01": round(float(np.percentile([row["timing_residual_rms_s"] for row in all_rows], 1)), 6),
            "p05": round(float(np.percentile([row["timing_residual_rms_s"] for row in all_rows], 5)), 6),
            "median": round(float(np.median([row["timing_residual_rms_s"] for row in all_rows])), 6),
        },
        "trajectory_cosine_distribution": {
            "median": round(float(np.median([row["descriptor_trajectory_cosine"] for row in all_rows])), 4),
            "p95": round(float(np.percentile([row["descriptor_trajectory_cosine"] for row in all_rows], 95)), 4),
            "p99": round(float(np.percentile([row["descriptor_trajectory_cosine"] for row in all_rows], 99)), 4),
        },
    }


def main() -> None:
    album = extract_events(decode(Path(ALBUM)))
    cops = extract_events(decode(Path(COPS)))
    pairs = one_to_one_match(album.times, cops.times, CANDIDATE_LAG_S, TOLERANCE_S)
    run = max(consecutive_runs(pairs), key=len)
    length = len(run)
    ai, bj = run[0][0], run[0][1]
    candidate = metrics(album, cops, ai, bj, length)
    all_rows = [
        metrics(album, cops, a_start, b_start, length)
        for a_start in range(len(album.times) - length + 1)
        for b_start in range(len(cops.times) - length + 1)
    ]
    report = {
        "analysis_date_utc": "2026-09-04",
        "source_previews_sha256": SOURCE_HASHES,
        "candidate_selection": {
            "source": "longest consecutive event-index run at the prior +1.31-second lag candidate",
            "matching_tolerance_s": TOLERANCE_S,
        },
        "candidate": candidate,
        "all_contiguous_subsequence_control": rank_against_all(candidate, all_rows),
        "interpretation": {
            "timing_question": "Can the sequence be explained by similar periodic spacing alone?",
            "descriptor_question": "Do relative spectral-event changes occur in the same order?",
            "decision_rule": "Treat as a localized shared-unit candidate only if timing and descriptor trajectory are both unusually strong; do not infer sample identity.",
        },
        "limits": [
            "all controls come from the same two approximately 30-second previews",
            "the candidate was selected from these data, so ranks are descriptive rather than confirmatory p-values",
            "event descriptors contain only four broad bands, centroid, and RMS",
            "preview source positions and full-track context are unknown",
            "no listening judgment or sample identity is claimed",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
