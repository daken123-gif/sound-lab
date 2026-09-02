#!/usr/bin/env python3
"""Audio-only evidence streams for synthetic cases S09-S12."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

from baseline_analyzer import detect_onsets, load_wav, periodic_hypotheses
from contextual_analyzer import event_spectrum, local_rms


def analyze_spatial_periodicity(
    audio: np.ndarray, sample_rate: int, onsets: np.ndarray
) -> dict:
    if audio.shape[1] < 2 or onsets.size < 4:
        return {"status": "insufficient_stereo_evidence"}
    balances = []
    for time in onsets:
        left = local_rms(audio[:, 0], sample_rate, float(time), 0.04)
        right = local_rms(audio[:, 1], sample_rate, float(time), 0.04)
        balances.append((right - left) / (right + left + 1e-12))
    balances_array = np.asarray(balances)
    event_period = float(np.median(np.diff(onsets)))
    candidates = []
    scale = float(np.std(balances_array)) + 1e-12
    for lag in range(1, min(8, balances_array.size // 2) + 1):
        error = float(np.sqrt(np.mean((balances_array[lag:] - balances_array[:-lag]) ** 2)))
        similarity = max(-1.0, 1.0 - error / (2.0 * scale))
        candidates.append(
            {
                "event_lag": lag,
                "period_seconds": round(lag * event_period, 6),
                "balance_similarity": round(similarity, 6),
            }
        )
    cycle = next((row for row in candidates if row["balance_similarity"] >= 0.9), None)
    return {
        "analysis_order": "stereo_before_mono",
        "mono_onset_period_seconds": round(event_period, 6),
        "signed_channel_balances": [round(float(value), 6) for value in balances_array],
        "spatial_cycle": cycle,
        "candidate_lags": candidates,
        "non_inference": "mono onset periodicity does not contain the alternating spatial relation",
    }


def split_constant_runs(values: np.ndarray, relative_threshold: float = 0.08) -> list[slice]:
    if values.size == 0:
        return []
    threshold = max(1e-9, float(np.max(np.abs(values))) * relative_threshold)
    cuts = np.where(np.abs(np.diff(values)) > threshold)[0] + 1
    starts = np.r_[0, cuts]
    ends = np.r_[cuts, values.size]
    return [slice(int(start), int(end)) for start, end in zip(starts, ends)]


def analyze_repetition_transformation(
    signal: np.ndarray,
    sample_rate: int,
    onsets: np.ndarray,
    strengths: np.ndarray,
) -> dict:
    runs = split_constant_runs(strengths)
    cycles = []
    offset_profiles = []
    amplitude_profiles = []
    pitch_profiles = []
    for index, run in enumerate(runs):
        times = onsets[run]
        if times.size < 2:
            continue
        offsets = times - times[0]
        peaks = [event_spectrum(signal, sample_rate, float(time), 0.08) for time in times]
        amplitude = float(np.median(strengths[run]))
        pitch = float(np.median([row["dominant_hz"] for row in peaks]))
        offset_profiles.append(offsets)
        amplitude_profiles.append(amplitude)
        pitch_profiles.append(pitch)
        cycles.append(
            {
                "index": index,
                "start_seconds": round(float(times[0]), 6),
                "onset_offsets_seconds": [round(float(value), 6) for value in offsets],
                "median_onset_strength": round(amplitude, 6),
                "dominant_frequency_hz": round(pitch, 6),
            }
        )
    comparable = len(offset_profiles) >= 2 and len({row.size for row in offset_profiles}) == 1
    topology_error = (
        max(
            float(np.max(np.abs(profile - offset_profiles[0])))
            for profile in offset_profiles[1:]
        )
        if comparable
        else None
    )
    amplitude_range = (
        float(max(amplitude_profiles) - min(amplitude_profiles))
        if amplitude_profiles
        else 0.0
    )
    pitch_range = float(max(pitch_profiles) - min(pitch_profiles)) if pitch_profiles else 0.0
    transformed = bool(
        comparable
        and topology_error is not None
        and topology_error <= 0.02
        and amplitude_range > 0.01
    )
    return {
        "cycles": cycles,
        "onset_topology_max_error_seconds": round(topology_error, 6) if topology_error is not None else None,
        "onset_strength_range": round(amplitude_range, 6),
        "dominant_frequency_range_hz": round(pitch_range, 6),
        "hypothesis": (
            "rhythmic_repetition_with_dynamics_transformation"
            if transformed
            else "insufficient_repetition_evidence"
        ),
        "exact_audio_repeat": False if transformed else None,
    }


def analyze_cycle_drift(onsets: np.ndarray, strengths: np.ndarray) -> dict:
    if onsets.size < 8:
        return {"cycles": [], "time_varying": False}
    threshold = (float(np.min(strengths)) + float(np.max(strengths))) / 2.0
    anchor_indices = np.where(strengths > threshold)[0]
    cycles = []
    for position, start_index in enumerate(anchor_indices):
        end_index = (
            int(anchor_indices[position + 1])
            if position + 1 < anchor_indices.size
            else onsets.size
        )
        times = onsets[start_index:end_index]
        if times.size < 2:
            continue
        if position + 1 < anchor_indices.size:
            period = float(onsets[anchor_indices[position + 1]] - onsets[start_index])
            evidence = "anchor_to_anchor"
        else:
            period = float(np.median(np.diff(times)) * times.size)
            evidence = "within_cycle_subdivision_extrapolation"
        cycles.append(
            {
                "index": position,
                "start_seconds": round(float(times[0]), 6),
                "period_seconds": round(period, 6),
                "event_count": int(times.size),
                "period_evidence": evidence,
            }
        )
    periods = np.asarray([row["period_seconds"] for row in cycles], dtype=float)
    slope = float(np.polyfit(np.arange(periods.size), periods, 1)[0]) if periods.size >= 2 else 0.0
    return {
        "cycles": cycles,
        "period_summary_median_seconds": round(float(np.median(periods)), 6) if periods.size else None,
        "period_trend_seconds_per_cycle": round(slope, 6),
        "time_varying": bool(periods.size >= 3 and np.ptp(periods) >= 0.2),
        "non_inference": "median period is a summary and does not replace cycle-local periods",
    }


def global_resonances(
    signal: np.ndarray,
    sample_rate: int,
    low_hz: float = 55.0,
    high_hz: float = 140.0,
    limit: int = 8,
) -> list[dict]:
    windowed = signal * np.hanning(signal.size)
    spectrum = np.abs(np.fft.rfft(windowed))
    frequencies = np.fft.rfftfreq(signal.size, 1.0 / sample_rate)
    mask = (frequencies >= low_hz) & (frequencies <= high_hz)
    selected = spectrum[mask]
    selected_frequencies = frequencies[mask]
    peaks, _ = find_peaks(
        selected,
        distance=max(1, round(0.25 / (sample_rate / signal.size))),
        prominence=float(np.max(selected)) * 0.01,
    )
    rows = [
        {
            "frequency_hz": round(float(selected_frequencies[index]), 6),
            "relative_magnitude": round(float(selected[index] / np.max(selected)), 6),
        }
        for index in peaks
    ]
    rows.sort(key=lambda row: row["relative_magnitude"], reverse=True)
    return rows[:limit]


def analyze_overlap_uncertainty(
    signal: np.ndarray,
    sample_rate: int,
    onsets: np.ndarray,
) -> dict:
    resonances = global_resonances(signal, sample_rate)
    primary = resonances[:2]
    separation = (
        abs(primary[0]["frequency_hz"] - primary[1]["frequency_hz"])
        if len(primary) == 2
        else None
    )
    periods = periodic_hypotheses(signal, sample_rate)[:5]
    return {
        "overlap_band_hz": [55.0, 140.0],
        "resonance_candidates": resonances,
        "primary_resonance_separation_hz": round(float(separation), 6) if separation is not None else None,
        "energy_flux_onset_count": int(onsets.size),
        "period_hypotheses": periods,
        "source_assignment": None,
        "identity_status": "unresolved_from_mixture",
        "separation_status": "model_hypothesis_not_observed_ground_truth",
        "non_inference": "resonance candidates are not named kick or bass stems",
    }


def analyze(path: Path) -> dict:
    sample_rate, audio = load_wav(path)
    mono = np.mean(audio, axis=1)
    onsets, strengths, _, _ = detect_onsets(mono, sample_rate, minimum_spacing=0.07)
    return {
        "analyzer": "extended-relational-evidence-v0.1",
        "audio": path.name,
        "spatial_periodicity": analyze_spatial_periodicity(audio, sample_rate, onsets),
        "repetition_transformation": analyze_repetition_transformation(
            mono, sample_rate, onsets, strengths
        ),
        "cycle_drift": analyze_cycle_drift(onsets, strengths),
        "overlap_uncertainty": analyze_overlap_uncertainty(mono, sample_rate, onsets),
        "limitations": [
            "synthetic_audio_thresholds",
            "stereo_balance_is_not_source_localization",
            "dynamics_runs_require_piecewise_stable_strength",
            "cycle_anchor_detection_requires_accent_contrast",
            "mixture_resonances_do_not_identify_sources",
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
