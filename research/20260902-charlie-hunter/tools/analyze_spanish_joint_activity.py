#!/usr/bin/env python3
"""Measure band activity, gaps, and handoffs in a Spanish Joint preview.

The measurements are proxies from a mastered stereo mix. They are not note
durations, stems, transcriptions, or performer-specific measurements.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import gaussian_filter1d, median_filter
from scipy.signal import stft


BANDS = {
    "low_45_180_hz": (45.0, 180.0),
    "low_mid_180_800_hz": (180.0, 800.0),
    "presence_800_3000_hz": (800.0, 3000.0),
    "high_3000_12000_hz": (3000.0, 12000.0),
}
FRAME_SIZE = 2048
HOP = 256
THRESHOLD_DB = -12.0
MIN_RUN_SECONDS = 0.04
MAX_GAP_SECONDS = 0.05


def runs(mask: np.ndarray) -> list[tuple[bool, int, int]]:
    """Return (value, start, end-exclusive) runs."""
    if len(mask) == 0:
        return []
    changes = np.flatnonzero(mask[1:] != mask[:-1]) + 1
    starts = np.r_[0, changes]
    ends = np.r_[changes, len(mask)]
    return [(bool(mask[start]), int(start), int(end)) for start, end in zip(starts, ends)]


def clean_activity(mask: np.ndarray, rate: int, hop: int) -> np.ndarray:
    """Fill very short holes, then reject very short activity spikes."""
    cleaned = mask.astype(bool).copy()
    max_gap = max(1, round(MAX_GAP_SECONDS * rate / hop))
    for value, start, end in runs(cleaned):
        if not value and start > 0 and end < len(cleaned) and end - start <= max_gap:
            cleaned[start:end] = True
    min_run = max(1, round(MIN_RUN_SECONDS * rate / hop))
    for value, start, end in runs(cleaned):
        if value and end - start < min_run:
            cleaned[start:end] = False
    return cleaned


def activity_envelopes(path: Path) -> tuple[int, int, dict[str, np.ndarray], dict[str, np.ndarray]]:
    rate, audio = wavfile.read(path)
    if audio.ndim == 2:
        audio = audio.astype(np.float64).mean(axis=1)
    else:
        audio = audio.astype(np.float64)
    audio /= max(1.0, np.max(np.abs(audio)))
    frequencies, _, spectrum = stft(
        audio,
        fs=rate,
        window="hann",
        nperseg=FRAME_SIZE,
        noverlap=FRAME_SIZE - HOP,
        nfft=FRAME_SIZE,
        boundary=None,
        padded=False,
    )
    power = np.abs(spectrum) ** 2
    relative_db: dict[str, np.ndarray] = {}
    activity: dict[str, np.ndarray] = {}
    for name, (low, high) in BANDS.items():
        selected = (frequencies >= low) & (frequencies < high)
        energy = power[selected].sum(axis=0)
        db = 10.0 * np.log10(energy + 1e-15)
        db -= np.percentile(db, 95)
        smoothed = gaussian_filter1d(median_filter(db, size=5), 2.0)
        relative_db[name] = smoothed
        activity[name] = clean_activity(smoothed >= THRESHOLD_DB, rate, HOP)
    return rate, HOP, relative_db, activity


def duration_summary(mask: np.ndarray, value: bool, rate: int, hop: int) -> dict:
    durations = [(end - start) * hop / rate for state, start, end in runs(mask) if state is value]
    if not durations:
        return {"count": 0, "total_seconds": 0.0, "share": 0.0}
    return {
        "count": len(durations),
        "total_seconds": round(float(sum(durations)), 3),
        "share": round(float(sum(durations) / (len(mask) * hop / rate)), 4),
        "median_ms": round(float(np.median(durations) * 1000.0), 1),
        "q25_ms": round(float(np.percentile(durations, 25) * 1000.0), 1),
        "q75_ms": round(float(np.percentile(durations, 75) * 1000.0), 1),
        "longest_ms": round(float(max(durations) * 1000.0), 1),
    }


def pair_states(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    # 0 neither, 1 first only, 2 second only, 3 both
    return first.astype(np.uint8) + 2 * second.astype(np.uint8)


def state_summary(states: np.ndarray) -> dict:
    labels = {0: "neither", 1: "low_only", 2: "low_mid_only", 3: "both"}
    shares = {labels[value]: round(float(np.mean(states == value)), 4) for value in labels}
    state_runs: list[int] = []
    if len(states):
        state_runs = [int(states[0])]
        for value in states[1:]:
            if int(value) != state_runs[-1]:
                state_runs.append(int(value))
    transitions: dict[str, int] = {}
    for first, second in zip(state_runs, state_runs[1:]):
        key = f"{labels[first]}__to__{labels[second]}"
        transitions[key] = transitions.get(key, 0) + 1
    return {"frame_shares": shares, "compressed_transition_counts": dict(sorted(transitions.items()))}


def threshold_sensitivity(relative_db: dict[str, np.ndarray], rate: int, hop: int) -> list[dict]:
    output = []
    for threshold in (-9.0, -12.0, -15.0):
        masks = {
            name: clean_activity(values >= threshold, rate, hop)
            for name, values in relative_db.items()
        }
        low = masks["low_45_180_hz"]
        low_mid = masks["low_mid_180_800_hz"]
        output.append({
            "threshold_db": threshold,
            "band_activity_shares": {
                name: round(float(np.mean(mask)), 4) for name, mask in masks.items()
            },
            "low_vs_low_mid_frame_shares": state_summary(pair_states(low, low_mid))["frame_shares"],
        })
    return output


def windowed_pair_activity(first: np.ndarray, second: np.ndarray, rate: int, hop: int) -> list[dict]:
    window = round(4.0 * rate / hop)
    step = round(2.0 * rate / hop)
    output = []
    for start in range(0, max(1, len(first) - window + 1), step):
        end = min(len(first), start + window)
        summary = state_summary(pair_states(first[start:end], second[start:end]))
        output.append({
            "start_seconds": round(start * hop / rate, 3),
            "end_seconds": round(end * hop / rate, 3),
            **summary["frame_shares"],
        })
    return output


def analyze(wav_path: Path, source_path: Path | None = None) -> dict:
    rate, hop, relative_db, activity = activity_envelopes(wav_path)
    band_summaries = {}
    for name, mask in activity.items():
        band_summaries[name] = {
            "activity_episodes": duration_summary(mask, True, rate, hop),
            "inactivity_gaps": duration_summary(mask, False, rate, hop),
            "relative_db_percentiles": {
                str(q): round(float(np.percentile(relative_db[name], q)), 3)
                for q in (5, 25, 50, 75, 95)
            },
        }
    low = activity["low_45_180_hz"]
    low_mid = activity["low_mid_180_800_hz"]
    states = pair_states(low, low_mid)
    duration = len(low) * hop / rate
    return {
        "schema_version": "sound-lab.spanish-joint-preview-activity/v1",
        "evidence_boundary": (
            "Thirty-second Apple Music catalog preview; mastered-mix band-activity proxies only. "
            "No source separation, note-duration transcription, or attribution to Charlie Hunter, "
            "Questlove, D'Angelo, horns, percussion, or any individual instrument."
        ),
        "method": {
            "frame_size": FRAME_SIZE,
            "hop": hop,
            "frame_step_ms": round(hop / rate * 1000.0, 3),
            "activity_threshold_db_relative_to_band_p95": THRESHOLD_DB,
            "median_filter_frames": 5,
            "gaussian_sigma_frames": 2.0,
            "fill_gaps_at_most_ms": MAX_GAP_SECONDS * 1000.0,
            "reject_activity_shorter_than_ms": MIN_RUN_SECONDS * 1000.0,
        },
        "audio": {
            "analyzed_duration_seconds": round(duration, 3),
            "sample_rate": rate,
            "wav_sha256": hashlib.sha256(wav_path.read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest() if source_path else None,
        },
        "bands": band_summaries,
        "threshold_sensitivity": threshold_sensitivity(relative_db, rate, hop),
        "low_vs_low_mid": {
            **state_summary(states),
            "windows": windowed_pair_activity(low, low_mid, rate, hop),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wav", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(analyze(args.wav, args.source), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
