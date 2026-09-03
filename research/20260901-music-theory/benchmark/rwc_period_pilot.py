#!/usr/bin/env python3
"""Run a bounded S01 period-candidate pilot on the RWC-R audio subset."""

from __future__ import annotations

import argparse
import csv
import io
import json
import wave
import zipfile
from pathlib import Path
from typing import Any

import numpy as np

from baseline_analyzer import detect_onsets, periodic_hypotheses


RATIOS = (0.25, 0.5, 1.0, 2.0, 3.0, 4.0)


def read_metadata(path: Path, subset: str) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    return sorted(
        (row for row in rows if row["CollID"] == subset),
        key=lambda row: row["RWCID"],
    )


def read_reference_beats(path: Path, start: float, end: float) -> np.ndarray:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    return np.asarray(
        [float(row["t"]) for row in rows if start <= float(row["t"]) <= end],
        dtype=float,
    )


def read_wav_excerpt(
    archive: zipfile.ZipFile, member: str, start: float, duration: float
) -> tuple[int, np.ndarray]:
    with archive.open(member) as compressed:
        with wave.open(io.BytesIO(compressed.read()), "rb") as wav:
            if wav.getsampwidth() != 2:
                raise ValueError(f"{member}: expected 16-bit PCM")
            sample_rate = wav.getframerate()
            channels = wav.getnchannels()
            first_frame = min(round(start * sample_rate), wav.getnframes())
            wav.setpos(first_frame)
            raw = wav.readframes(round(duration * sample_rate))
    values = np.frombuffer(raw, dtype="<i2")
    audio = values.astype(np.float64).reshape(-1, channels) / 32768.0
    return sample_rate, audio


def relate_candidates(candidates: list[dict], reference_period: float) -> dict[str, Any]:
    related = []
    direct_rank = None
    for rank, candidate in enumerate(candidates, start=1):
        period = float(candidate["period"])
        ratio = period / reference_period
        nearest = min(RATIOS, key=lambda value: abs(ratio - value))
        relative_error = abs(ratio - nearest) / nearest
        if relative_error <= 0.04:
            row = {
                "rank": rank,
                "period": period,
                "ratio_to_reference": round(ratio, 6),
                "nearest_meter_ratio": nearest,
                "relative_error": round(relative_error, 6),
            }
            related.append(row)
            if nearest == 1.0 and direct_rank is None:
                direct_rank = rank
    return {"direct_match_rank": direct_rank, "meter_related_candidates": related}


def run_pilot(
    audio_zip: Path,
    annotations_root: Path,
    subset: str = "R",
    offset_seconds: float = 5.0,
    excerpt_seconds: float = 20.0,
) -> dict[str, Any]:
    metadata_rows = read_metadata(annotations_root / "metadata.csv", subset)
    tracks = []
    with zipfile.ZipFile(audio_zip) as archive:
        for metadata in metadata_rows:
            recording_id = metadata["RWCID"]
            music_start = float(metadata["audio_start"])
            music_end = float(metadata["audio_end"])
            start = min(music_start + offset_seconds, max(music_start, music_end - excerpt_seconds))
            duration = min(excerpt_seconds, music_end - start)
            sample_rate, audio = read_wav_excerpt(
                archive,
                f"RWC-{subset}/{recording_id}.wav",
                start,
                duration,
            )
            mono = np.mean(audio, axis=1)
            onset_times, _strengths, _times, _envelope = detect_onsets(mono, sample_rate)
            candidates = periodic_hypotheses(mono, sample_rate)
            beat_path = (
                annotations_root
                / "01_annotations_preprocessed"
                / "beats"
                / f"RWC-{subset}"
                / f"{recording_id}.csv"
            )
            beats = read_reference_beats(beat_path, start, start + duration)
            if beats.size < 3:
                raise ValueError(f"{recording_id}: too few reference beats in excerpt")
            reference_period = float(np.median(np.diff(beats)))
            relation = relate_candidates(candidates, reference_period)
            tracks.append(
                {
                    "recording_id": recording_id,
                    "excerpt_start_seconds": round(start, 6),
                    "excerpt_duration_seconds": round(duration, 6),
                    "reference_beats": int(beats.size),
                    "reference_period_seconds": round(reference_period, 6),
                    "reference_bpm": round(60.0 / reference_period, 6),
                    "detected_onsets": int(onset_times.size),
                    "candidate_count": len(candidates),
                    "top_candidate_period_seconds": (
                        float(candidates[0]["period"]) if candidates else None
                    ),
                    **relation,
                }
            )
    direct = sum(track["direct_match_rank"] is not None for track in tracks)
    related = sum(bool(track["meter_related_candidates"]) for track in tracks)
    return {
        "status": "pilot_executed",
        "scope": {
            "subset": subset,
            "tracks": len(tracks),
            "offset_seconds": offset_seconds,
            "excerpt_seconds": excerpt_seconds,
            "analyzer": "scipy energy-flux autocorrelation baseline",
            "tolerance": "4% around ratios 0.25, 0.5, 1, 2, 3, 4",
        },
        "summary": {
            "direct_reference_period_found": direct,
            "any_meter_related_period_found": related,
            "top_rank_direct_matches": sum(
                track["direct_match_rank"] == 1 for track in tracks
            ),
        },
        "tracks": tracks,
        "limitations": [
            "bounded_20_second_excerpts",
            "rwc_royalty_free_subset_only",
            "beat_annotations_used_only_after_audio_candidate_estimation",
            "period_relation_is_not_perceptual_meter_ground_truth",
            "no_librosa_frontend_in_this_pilot",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-zip", type=Path, required=True)
    parser.add_argument("--annotations-root", type=Path, required=True)
    parser.add_argument("--subset", default="R")
    parser.add_argument("--offset-seconds", type=float, default=5.0)
    parser.add_argument("--excerpt-seconds", type=float, default=20.0)
    args = parser.parse_args()
    result = run_pilot(
        args.audio_zip,
        args.annotations_root,
        args.subset,
        args.offset_seconds,
        args.excerpt_seconds,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
