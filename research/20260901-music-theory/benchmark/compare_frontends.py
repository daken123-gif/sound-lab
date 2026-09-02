#!/usr/bin/env python3
"""Compare the transparent SciPy and librosa 1.0 audio frontends."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import librosa
import numpy as np
import scipy

from baseline_analyzer import analyze as analyze_scipy
from librosa_analyzer import analyze as analyze_librosa


CASES = ("s01", "s02", "s03", "s04")
EXPECTED_ONSET_COUNTS = {"s01": 18, "s02": 19, "s03": 19, "s04": 22}


def contains_period(rows: list[dict], target: float, tolerance: float = 0.04) -> bool:
    return any(abs(row["period"] - target) <= tolerance for row in rows)


def evaluate(case: str, result: dict) -> dict:
    checks: dict[str, bool] = {
        "onset_count_matches": len(result["onsets"]) == EXPECTED_ONSET_COUNTS[case]
    }
    if case == "s01":
        checks["period_0.5_retained"] = contains_period(result["period_hypotheses"], 0.5)
        checks["period_1.0_retained"] = contains_period(result["period_hypotheses"], 1.0)
    elif case == "s02":
        checks["cycle_2.0_retained"] = contains_period(result["period_hypotheses"], 2.0)
        nearest = min(result["period_hypotheses"], key=lambda row: abs(row["period"] - 2.0))
        checks["cycle_phase_present"] = nearest.get("phase") is not None
    elif case == "s03":
        left = result["channel_analysis"][0]["period_hypotheses"]
        right = result["channel_analysis"][1]["period_hypotheses"]
        checks["left_0.75_retained"] = contains_period(left, 0.75)
        checks["right_1.0_retained"] = contains_period(right, 1.0)
    elif case == "s04":
        curve = result["low_band_tempo_curve"]
        residuals = result["cross_band_timing_residuals_ms"]
        checks["tempo_curve_present"] = curve is not None
        checks["acceleration_detected"] = bool(
            curve and curve["period_end"] < curve["period_start"]
        )
        checks["negative_residual_present"] = any(value < -3 for value in residuals)
        checks["positive_residual_present"] = any(value > 3 for value in residuals)
    return {"passed": all(checks.values()), "checks": checks}


def summarize(result: dict) -> dict:
    curve = result["low_band_tempo_curve"]
    return {
        "period_hypotheses": [
            {
                "period": row["period"],
                "score": row["score"],
                "phase": row.get("phase"),
            }
            for row in result["period_hypotheses"]
        ],
        "onset_count": len(result["onsets"]),
        "tempo_curve": curve,
        "timing_residuals_ms": result["cross_band_timing_residuals_ms"],
    }


def timed(analyzer, path: Path, repeats: int) -> tuple[dict, list[float]]:
    analyzer(path)
    durations = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = analyzer(path)
        durations.append((time.perf_counter() - start) * 1000.0)
    assert result is not None
    return result, durations


def compare(audio_dir: Path, repeats: int = 3) -> dict:
    engines = {
        "scipy_baseline": analyze_scipy,
        "librosa_1.0": analyze_librosa,
    }
    payload = {
        "comparison": "music-theory-audio-frontends-v0.1",
        "repeats_after_warmup": repeats,
        "versions": {
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "librosa": librosa.__version__,
        },
        "engines": {},
    }
    for engine_name, analyzer in engines.items():
        engine_rows = {}
        for case in CASES:
            result, durations = timed(analyzer, audio_dir / f"{case}.wav", repeats)
            engine_rows[case] = {
                "evaluation": evaluate(case, result),
                "runtime_ms": {
                    "median": round(statistics.median(durations), 3),
                    "min": round(min(durations), 3),
                    "max": round(max(durations), 3),
                    "samples": [round(value, 3) for value in durations],
                },
                "output": summarize(result),
            }
        payload["engines"][engine_name] = engine_rows
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-dir", type=Path, default=Path(__file__).with_name("generated"))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = compare(args.audio_dir, args.repeats)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
