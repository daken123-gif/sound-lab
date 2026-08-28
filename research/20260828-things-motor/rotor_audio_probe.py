#!/usr/bin/env python3
"""Render synthetic four-track material through candidate Rotor curves."""

from __future__ import annotations

import argparse
import json
import math
import struct
import wave
from pathlib import Path

from rotor_measure import (
    adjacent_pair,
    correlation_compensated_gains,
    crossfade_gains,
    db,
)


def rms(samples: list[float]) -> float:
    if not samples:
        return 0.0
    return math.sqrt(sum(sample * sample for sample in samples) / len(samples))


def peak(samples: list[float]) -> float:
    return max((abs(sample) for sample in samples), default=0.0)


def pearson(first: list[float], second: list[float]) -> float:
    if len(first) != len(second) or not first:
        raise ValueError("correlation inputs must have the same non-zero length")
    first_mean = sum(first) / len(first)
    second_mean = sum(second) / len(second)
    numerator = 0.0
    first_energy = 0.0
    second_energy = 0.0
    for a, b in zip(first, second):
        a -= first_mean
        b -= second_mean
        numerator += a * b
        first_energy += a * a
        second_energy += b * b
    denominator = math.sqrt(first_energy * second_energy)
    if denominator == 0.0:
        return 0.0
    return max(-1.0, min(1.0, numerator / denominator))


def sine(
    frequency: float,
    frames: int,
    sample_rate: float,
    *,
    phase: float = 0.0,
    amplitude: float = 0.25,
) -> list[float]:
    return [
        amplitude * math.sin(2.0 * math.pi * frequency * index / sample_rate + phase)
        for index in range(frames)
    ]


def material_cases(sample_rate: int = 48_000, seconds: float = 4.0) -> dict[str, list[list[float]]]:
    frames = round(sample_rate * seconds)
    shared = sine(220.0, frames, sample_rate)
    return {
        "identical": [shared.copy() for _ in range(4)],
        "strongly_correlated": [
            sine(220.0, frames, sample_rate, phase=phase)
            for phase in (0.0, 0.25, 0.50, 0.75)
        ],
        "unrelated": [
            sine(frequency, frames, sample_rate)
            for frequency in (173.0, 257.0, 389.0, 541.0)
        ],
        "silence_mixed": [
            sine(220.0, frames, sample_rate),
            [0.0] * frames,
            sine(331.0, frames, sample_rate),
            [0.0] * frames,
        ],
    }


def adjacent_correlations(tracks: list[list[float]]) -> list[float]:
    return [pearson(tracks[index], tracks[(index + 1) % len(tracks)]) for index in range(len(tracks))]


def render(tracks: list[list[float]], mode: str) -> tuple[list[float], list[float]]:
    if len(tracks) != 4 or len({len(track) for track in tracks}) != 1:
        raise ValueError("render expects four equal-length tracks")
    frame_count = len(tracks[0])
    correlations = adjacent_correlations(tracks)
    output: list[float] = []
    for frame in range(frame_count):
        phase = frame / frame_count
        current, following, local = adjacent_pair(phase, len(tracks))
        if mode == "correlation_compensated":
            first, second = correlation_compensated_gains(
                local, correlations[current]
            )
        else:
            first, second = crossfade_gains(local, mode)
        output.append(
            first * tracks[current][frame] + second * tracks[following][frame]
        )
    return output, correlations


def write_wav(path: Path, samples: list[float], sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        payload = bytearray()
        for sample in samples:
            clipped = min(1.0, max(-1.0, sample))
            payload.extend(struct.pack("<h", round(clipped * 32767.0)))
        output.writeframes(payload)


def probe(sample_rate: int = 48_000, seconds: float = 4.0, wav_dir: Path | None = None) -> dict[str, object]:
    report: dict[str, object] = {
        "sample_rate": sample_rate,
        "seconds": seconds,
        "rotations": 1.0,
        "cases": {},
    }
    for case_name, tracks in material_cases(sample_rate, seconds).items():
        non_silent_rms = [value for value in map(rms, tracks) if value > 0.0]
        baseline_rms = sum(non_silent_rms) / len(non_silent_rms)
        case_report: dict[str, object] = {}
        for mode in ("equal_power", "linear", "correlation_compensated"):
            output, correlations = render(tracks, mode)
            output_rms = rms(output)
            case_report[mode] = {
                "adjacent_correlations": correlations,
                "rms": output_rms,
                "rms_relative_to_non_silent_track_db": db(output_rms / baseline_rms),
                "peak": peak(output),
            }
            if wav_dir is not None:
                write_wav(wav_dir / f"{case_name}--{mode}.wav", output, sample_rate)
        report["cases"][case_name] = case_report
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav-dir", type=Path)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            probe(wav_dir=args.wav_dir),
            indent=None if args.compact else 2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
