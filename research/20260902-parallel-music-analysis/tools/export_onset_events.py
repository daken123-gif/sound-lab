#!/usr/bin/env python3
"""Export inspectable onset candidates from a PCM WAV file.

This tool does not assign instrument roles and does not invent a beat origin.
Clock-relative fields are emitted only when both BPM and beat origin are given.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import wave
from pathlib import Path

import numpy as np


def load_pcm_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_rate = handle.getframerate()
        sample_width = handle.getsampwidth()
        frames = handle.readframes(handle.getnframes())

    if sample_width == 1:
        audio = (np.frombuffer(frames, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
    elif sample_width == 2:
        audio = np.frombuffer(frames, dtype="<i2").astype(np.float64) / 32768.0
    elif sample_width == 4:
        audio = np.frombuffer(frames, dtype="<i4").astype(np.float64) / 2147483648.0
    else:
        raise ValueError(f"unsupported PCM sample width: {sample_width} bytes")

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    return audio, sample_rate


def frame_rms(audio: np.ndarray, frame_size: int, hop_size: int) -> np.ndarray:
    if len(audio) == 0:
        return np.zeros(0, dtype=np.float64)
    padded = np.pad(audio, (0, max(0, frame_size - len(audio))))
    count = 1 + max(0, (len(padded) - frame_size) // hop_size)
    result = np.empty(count, dtype=np.float64)
    for index in range(count):
        frame = padded[index * hop_size : index * hop_size + frame_size]
        result[index] = float(np.sqrt(np.mean(frame * frame)))
    return result


def detect_onsets(
    audio: np.ndarray,
    sample_rate: int,
    frame_size: int = 1024,
    hop_size: int = 256,
    min_separation_s: float = 0.05,
) -> list[dict[str, float]]:
    rms = frame_rms(audio, frame_size, hop_size)
    if len(rms) < 2:
        return []
    novelty = np.maximum(0.0, np.diff(rms, prepend=rms[0]))
    median = float(np.median(novelty))
    mad = float(np.median(np.abs(novelty - median)))
    threshold = max(median + 4.0 * mad, 0.05 * float(novelty.max(initial=0.0)))
    peak_frames = [
        index
        for index in range(1, len(novelty) - 1)
        if novelty[index] >= threshold
        and novelty[index] >= novelty[index - 1]
        and novelty[index] > novelty[index + 1]
    ]

    maximum = float(novelty.max(initial=0.0)) or 1.0
    min_samples = max(1, int(round(min_separation_s * sample_rate)))
    candidates: list[tuple[int, float]] = []
    for frame_index in peak_frames:
        start = frame_index * hop_size
        stop = min(len(audio), start + frame_size)
        if stop <= start:
            continue
        sample_index = start + int(np.argmax(np.abs(audio[start:stop])))
        strength = float(novelty[frame_index] / maximum)
        if candidates and sample_index - candidates[-1][0] < min_samples:
            if strength > candidates[-1][1]:
                candidates[-1] = (sample_index, strength)
            continue
        candidates.append((sample_index, strength))

    return [
        {
            "absolute_time_s": round(sample_index / sample_rate, 6),
            "onset_confidence": round(strength, 6),
        }
        for sample_index, strength in candidates
    ]


def attach_clock(
    events: list[dict[str, object]], bpm: float | None, beat_origin_s: float | None
) -> None:
    if bpm is None or beat_origin_s is None:
        for event in events:
            event.update(
                {
                    "clock_candidate": None,
                    "beat_index": None,
                    "offset_from_clock_s": None,
                }
            )
        return

    period = 60.0 / bpm
    for event in events:
        time_s = float(event["absolute_time_s"])
        beat_index = int(round((time_s - beat_origin_s) / period))
        grid_time = beat_origin_s + beat_index * period
        event.update(
            {
                "clock_candidate": "provided_beat_grid",
                "beat_index": beat_index,
                "offset_from_clock_s": round(time_s - grid_time, 6),
            }
        )


def analyze_wav(
    path: Path,
    source_id: str,
    bpm: float | None = None,
    beat_origin_s: float | None = None,
) -> dict[str, object]:
    if (bpm is None) != (beat_origin_s is None):
        raise ValueError("bpm and beat_origin_s must be provided together")
    audio, sample_rate = load_pcm_wav(path)
    events: list[dict[str, object]] = [dict(row) for row in detect_onsets(audio, sample_rate)]
    attach_clock(events, bpm, beat_origin_s)
    for event in events:
        event.update(
            {
                "role": "unknown_onset",
                "separation_provenance": None,
                "original_mix_recheck": False,
            }
        )
    return {
        "schema": "parallel-onset-events-v1",
        "source": {
            "source_id": source_id,
            "file": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "sample_rate": sample_rate,
            "duration_s": round(len(audio) / sample_rate, 6),
        },
        "provided_clock": (
            None
            if bpm is None
            else {"bpm": bpm, "beat_origin_s": beat_origin_s, "authority": "caller-provided"}
        ),
        "events": events,
        "boundary": (
            "energy-rise candidates only; instrument role, beat/downbeat authority, "
            "and original-mix confirmation require human or independent evidence"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("wav", type=Path)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--bpm", type=float)
    parser.add_argument("--beat-origin-s", type=float)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = analyze_wav(args.wav, args.source_id, args.bpm, args.beat_origin_s)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
