#!/usr/bin/env python3
"""Audio-only evidence streams for synthetic cases S05-S08.

The analyser does not read ground-truth.json.  It emits observations and weak
relational hypotheses; it does not assign scalar groove quality or promote a
single feature change to a global musical boundary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from baseline_analyzer import band_signal, detect_onsets, load_wav


def best_split(values: np.ndarray, minimum_side: int = 3) -> tuple[int, float]:
    """Return the split with the largest standardized mean separation."""
    if values.size < minimum_side * 2:
        return 0, 0.0
    scale = float(np.std(values)) + 1e-12
    candidates = []
    for index in range(minimum_side, values.size - minimum_side + 1):
        effect = abs(float(np.mean(values[:index]) - np.mean(values[index:]))) / scale
        candidates.append((effect, index))
    effect, index = max(candidates)
    return index, effect


def event_spectrum(
    signal: np.ndarray, sample_rate: int, time: float, seconds: float = 0.1
) -> dict:
    size = int(seconds * sample_rate)
    start = int(round(time * sample_rate))
    chunk = signal[start : start + size]
    if chunk.size < size:
        chunk = np.pad(chunk, (0, size - chunk.size))
    windowed = chunk * np.hanning(size)
    spectrum = np.abs(np.fft.rfft(windowed))
    frequencies = np.fft.rfftfreq(size, 1.0 / sample_rate)
    mask = (frequencies >= 80.0) & (frequencies <= 5_000.0)
    selected = spectrum[mask]
    selected_frequencies = frequencies[mask]
    total = float(np.sum(selected)) + 1e-12
    centroid = float(np.sum(selected * selected_frequencies) / total)
    dominant = float(selected_frequencies[int(np.argmax(selected))])
    concentration = float(np.sort(selected)[-5:].sum() / total)
    return {
        "centroid_hz": centroid,
        "dominant_hz": dominant,
        "peak": float(np.max(np.abs(windowed))),
        "rms": float(np.sqrt(np.mean(windowed**2))),
        "spectral_concentration": concentration,
    }


def analyze_microtiming(onsets: np.ndarray) -> dict:
    if onsets.size < 4:
        return {"sections": [], "shape_relations": []}
    intervals = np.diff(onsets)
    typical = float(np.median(intervals))
    cut_indices = np.where(intervals > typical * 1.5)[0] + 1
    groups = np.split(onsets, cut_indices)
    sections = []
    profiles = []
    for index, group in enumerate(groups):
        if group.size < 3:
            continue
        steps = np.arange(group.size, dtype=float)
        period, phase = np.polyfit(steps, group, 1)
        residuals = group - (phase + period * steps)
        profiles.append(residuals)
        sections.append(
            {
                "index": index,
                "range_seconds": [round(float(group[0]), 6), round(float(group[-1]), 6)],
                "fitted_period_seconds": round(float(period), 6),
                "signed_residuals_ms": [round(float(value * 1_000.0), 3) for value in residuals],
                "mean_absolute_residual_ms": round(float(np.mean(np.abs(residuals)) * 1_000.0), 3),
                "quality_label": None,
            }
        )

    relations = []
    for left in range(len(profiles)):
        for right in range(left + 1, len(profiles)):
            if profiles[left].size != profiles[right].size:
                continue
            left_scale = float(np.mean(np.abs(profiles[left])))
            right_scale = float(np.mean(np.abs(profiles[right])))
            comparable = float(np.std(profiles[left])) > 1e-6 and float(np.std(profiles[right])) > 1e-6
            correlation = (
                float(np.corrcoef(profiles[left], profiles[right])[0, 1])
                if comparable
                else None
            )
            scale_ratio = right_scale / left_scale if left_scale > 1e-9 else None
            relations.append(
                {
                    "sections": [left, right],
                    "signed_shape_correlation": round(correlation, 6) if correlation is not None else None,
                    "absolute_scale_ratio": round(scale_ratio, 6) if scale_ratio else None,
                    "hypothesis": (
                        "insufficient_variation_for_shape_comparison"
                        if not comparable
                        else "scaled_timing_shape"
                        if correlation >= 0.9
                        else "different_timing_shape"
                    ),
                }
            )
    return {
        "sections": sections,
        "shape_relations": relations,
        "non_inference": "mean absolute residual is not groove quality",
    }


def analyze_feature_boundaries(
    signal: np.ndarray, sample_rate: int, onsets: np.ndarray
) -> dict:
    features = [event_spectrum(signal, sample_rate, float(time)) for time in onsets]
    if len(features) < 6:
        return {"streams": {}, "boundary_hypotheses": []}
    arrays = {
        "timbre_centroid": np.asarray([row["centroid_hz"] for row in features]),
        "dominant_pitch": np.asarray([row["dominant_hz"] for row in features]),
        "peak_amplitude": np.asarray([row["peak"] for row in features]),
    }
    streams = {}
    hypotheses = []
    for name, values in arrays.items():
        index, effect = best_split(values)
        before = float(np.median(values[:index])) if index else float(np.median(values))
        after = float(np.median(values[index:])) if index else before
        relative_change = abs(after - before) / (abs(before) + 1e-12)
        changed = effect >= 1.5 and relative_change >= 0.08
        boundary = float(onsets[index]) if changed and index < onsets.size else None
        streams[name] = {
            "before_median": round(before, 6),
            "after_median": round(after, 6),
            "relative_change": round(relative_change, 6),
            "changed": changed,
            "boundary_seconds": round(boundary, 6) if boundary is not None else None,
        }
        if changed:
            hypotheses.append(
                {
                    "time_seconds": round(boundary, 6),
                    "scope": name,
                    "global_boundary": False,
                }
            )

    intervals = np.diff(onsets)
    streams["rhythm_interval"] = {
        "median_seconds": round(float(np.median(intervals)), 6),
        "maximum_deviation_seconds": round(float(np.max(np.abs(intervals - np.median(intervals)))), 6),
        "changed": False,
        "boundary_seconds": None,
    }
    return {"streams": streams, "boundary_hypotheses": hypotheses}


def local_rms(signal: np.ndarray, sample_rate: int, time: float, seconds: float = 0.06) -> float:
    start = int(round(time * sample_rate))
    size = int(seconds * sample_rate)
    chunk = signal[start : start + size]
    return float(np.sqrt(np.mean(chunk**2))) if chunk.size else 0.0


def analyze_role_transfer(
    signal: np.ndarray, sample_rate: int, onsets: np.ndarray, strengths: np.ndarray
) -> dict:
    if onsets.size < 8:
        return {"anchor_events": [], "segments": [], "transfer_hypotheses": []}
    strong = strengths > float(np.median(strengths))
    anchors = onsets[strong]
    low = band_signal(signal, sample_rate, 100.0, 400.0)
    high = band_signal(signal, sample_rate, 800.0, 2_000.0)
    log_ratios = np.asarray(
        [
            np.log10(
                (local_rms(low, sample_rate, float(time)) + 1e-9)
                / (local_rms(high, sample_rate, float(time)) + 1e-9)
            )
            for time in anchors
        ]
    )
    index, effect = best_split(log_ratios)
    boundary = float(anchors[index]) if index else None
    segments = []
    for start, end in ((0, index), (index, anchors.size)) if index else ((0, anchors.size),):
        median_ratio = float(np.median(log_ratios[start:end]))
        segments.append(
            {
                "range_seconds": [
                    round(float(anchors[start]), 6),
                    round(float(anchors[end - 1]), 6),
                ],
                "pulse_anchor_band": "low" if median_ratio > 0 else "high",
                "median_log10_low_high_energy": round(median_ratio, 6),
            }
        )
    transfer = []
    if index and effect >= 1.5 and segments[0]["pulse_anchor_band"] != segments[1]["pulse_anchor_band"]:
        transfer.append(
            {
                "time_seconds": round(boundary, 6),
                "from_band": segments[0]["pulse_anchor_band"],
                "to_band": segments[1]["pulse_anchor_band"],
                "hypothesis": "pulse_anchor_role_transfer",
            }
        )
    return {
        "anchor_events": [round(float(value), 6) for value in anchors],
        "segments": segments,
        "transfer_hypotheses": transfer,
        "non_inference": "frequency band is evidence for a role, not a fixed instrument identity",
    }


def analyze_decay_boundaries(
    signal: np.ndarray, sample_rate: int, onsets: np.ndarray, strengths: np.ndarray
) -> dict:
    direct_mask = strengths >= float(np.max(strengths)) * 0.2 if strengths.size else np.array([], dtype=bool)
    direct_onsets = onsets[direct_mask]
    direct_end = float(direct_onsets[-1] + 0.03) if direct_onsets.size else None

    frame = int(0.05 * sample_rate)
    hop = int(0.01 * sample_rate)
    rms = np.asarray(
        [
            np.sqrt(np.mean(signal[start : start + frame] ** 2))
            for start in range(0, max(1, signal.size - frame + 1), hop)
        ]
    )
    threshold = float(np.max(rms) * 0.005) if rms.size else 0.0
    active = np.where(rms > threshold)[0]
    tail_end = float((active[-1] * hop + frame) / sample_rate) if active.size else None
    return {
        "direct_sound": {
            "supporting_onsets": [round(float(value), 6) for value in direct_onsets],
            "end_seconds": round(direct_end, 6) if direct_end is not None else None,
            "method": "strong_periodic_transients_plus_30ms_event_body",
        },
        "decay_tail": {
            "end_seconds": round(tail_end, 6) if tail_end is not None else None,
            "rms_threshold": round(threshold, 9),
            "threshold_relative_to_peak": 0.005,
            "method": "last_50ms_frame_above_relative_rms_threshold",
        },
        "non_inference": "tail threshold is an operational boundary, not a perceptual universal",
    }


def analyze(path: Path) -> dict:
    sample_rate, audio = load_wav(path)
    mono = np.mean(audio, axis=1)
    onsets, strengths, _, _ = detect_onsets(mono, sample_rate)
    return {
        "analyzer": "contextual-evidence-baseline-v0.1",
        "audio": path.name,
        "observed_onsets": [round(float(value), 6) for value in onsets],
        "microtiming": analyze_microtiming(onsets),
        "feature_boundaries": analyze_feature_boundaries(mono, sample_rate, onsets),
        "role_transfer": analyze_role_transfer(mono, sample_rate, onsets, strengths),
        "decay_boundaries": analyze_decay_boundaries(mono, sample_rate, onsets, strengths),
        "limitations": [
            "synthetic_audio_thresholds",
            "fixed_low_and_high_frequency_bands",
            "no_perceptual_listener_model",
            "role_and_boundary_outputs_are_hypotheses",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = [analyze(path) for path in args.audio]
    payload = results[0] if len(results) == 1 else results
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
