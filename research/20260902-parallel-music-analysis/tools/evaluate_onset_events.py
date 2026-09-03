#!/usr/bin/env python3
"""Evaluate onset-time candidates against human reference times."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def match_times(
    reference: list[float], estimated: list[float], tolerance_s: float = 0.05
) -> list[tuple[int, int]]:
    if tolerance_s < 0:
        raise ValueError("tolerance_s must be non-negative")
    ref = sorted(enumerate(reference), key=lambda item: item[1])
    est = sorted(enumerate(estimated), key=lambda item: item[1])

    # Dynamic programming gives a maximum-cardinality, order-preserving
    # one-to-one matching.  Among matchings with the same cardinality, prefer
    # the one with the smaller total timing error.  A nearest-neighbour greedy
    # pass can consume an estimate that is the only valid partner for the next
    # reference and therefore under-count true positives.
    # Each cell contains: (match_count, total_error, pairs).
    empty: tuple[int, float, tuple[tuple[int, int], ...]] = (0, 0.0, ())
    table = [[empty for _ in range(len(est) + 1)] for _ in range(len(ref) + 1)]

    def better(
        left: tuple[int, float, tuple[tuple[int, int], ...]],
        right: tuple[int, float, tuple[tuple[int, int], ...]],
    ) -> tuple[int, float, tuple[tuple[int, int], ...]]:
        if left[0] != right[0]:
            return left if left[0] > right[0] else right
        return left if left[1] <= right[1] else right

    for i in range(1, len(ref) + 1):
        for j in range(1, len(est) + 1):
            best = better(table[i - 1][j], table[i][j - 1])
            ref_index, ref_time = ref[i - 1]
            est_index, est_time = est[j - 1]
            error = abs(est_time - ref_time)
            if error <= tolerance_s:
                prior = table[i - 1][j - 1]
                matched = (prior[0] + 1, prior[1] + error, prior[2] + ((ref_index, est_index),))
                best = better(best, matched)
            table[i][j] = best

    return sorted(table[-1][-1][2])


def evaluate(
    reference: list[float], estimated: list[float], tolerance_s: float = 0.05
) -> dict[str, object]:
    matches = match_times(reference, estimated, tolerance_s)
    true_positive = len(matches)
    false_positive = len(estimated) - true_positive
    false_negative = len(reference) - true_positive
    precision = true_positive / len(estimated) if estimated else 0.0
    recall = true_positive / len(reference) if reference else 0.0
    f_measure = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tolerance_s": tolerance_s,
        "reference_count": len(reference),
        "estimated_count": len(estimated),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f_measure": round(f_measure, 6),
        "matches": [{"reference_index": r, "estimated_index": e} for r, e in matches],
        "boundary": (
            "A tolerance-window score measures agreement with these annotations; "
            "it does not establish perceptual, metrical, or instrument-role correctness."
        ),
    }


def load_reference(path: Path) -> list[float]:
    return [float(line.strip()) for line in path.read_text().splitlines() if line.strip()]


def load_estimated(path: Path) -> list[float]:
    data = json.loads(path.read_text())
    return [float(event["absolute_time_s"]) for event in data["events"]]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path, help="one reference onset time in seconds per line")
    parser.add_argument("estimated", type=Path, help="parallel onset-event JSON")
    parser.add_argument("--tolerance-s", type=float, default=0.05)
    args = parser.parse_args()
    print(
        json.dumps(
            evaluate(load_reference(args.reference), load_estimated(args.estimated), args.tolerance_s),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
