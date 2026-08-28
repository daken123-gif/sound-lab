#!/usr/bin/env python3
"""Run the moving Rotor switch probe on four external audio recordings."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from array import array
from pathlib import Path

from rotor_audio_probe import peak, rms, write_wav
from rotor_switch_probe import scenario_metrics


def decode_mono(path: Path, sample_rate: int) -> list[float]:
    """Decode an audio file to mono float32 with an explicit ffmpeg boundary."""
    if not path.is_file():
        raise ValueError(f"input does not exist: {path}")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is required to decode external recordings")
    completed = subprocess.run(
        [
            ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-i",
            str(path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-f",
            "f32le",
            "-acodec",
            "pcm_f32le",
            "pipe:1",
        ],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"ffmpeg could not decode {path.name}: {detail}")
    if len(completed.stdout) % 4:
        raise ValueError(f"decoder returned a partial float sample for {path.name}")
    samples = array("f")
    samples.frombytes(completed.stdout)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tolist()


def field_probe(
    paths: list[Path],
    *,
    sample_rate: int = 48_000,
    mode: str = "hold",
    speed_hz: float = 0.5,
    phase_at_switch: float = 0.8,
    switch_seconds: float = 0.2,
    ramp_ms: float = 5.0,
    output_ramped: Path | None = None,
    output_immediate: Path | None = None,
) -> dict[str, object]:
    if len(paths) != 4:
        raise ValueError("exactly four recordings are required")
    if sample_rate <= 0 or ramp_ms <= 0.0:
        raise ValueError("sample rate and ramp duration must be positive")

    decoded = [decode_mono(path, sample_rate) for path in paths]
    decoded_frames = [len(track) for track in decoded]
    frame_count = min(decoded_frames)
    switch_frame = round(switch_seconds * sample_rate)
    if frame_count <= switch_frame + 1:
        raise ValueError("recordings are too short for the requested switch time")
    tracks = [track[:frame_count] for track in decoded]
    ramp_frames = max(1, round(ramp_ms * sample_rate / 1_000.0))

    immediate_metrics, immediate = scenario_metrics(
        tracks,
        sample_rate=sample_rate,
        mode=mode,
        switch_frame=switch_frame,
        phase_at_switch=phase_at_switch,
        speed_hz=speed_hz,
        transition_frames=1,
    )
    ramped_metrics, ramped = scenario_metrics(
        tracks,
        sample_rate=sample_rate,
        mode=mode,
        switch_frame=switch_frame,
        phase_at_switch=phase_at_switch,
        speed_hz=speed_hz,
        transition_frames=ramp_frames,
    )
    if output_immediate is not None:
        write_wav(output_immediate, immediate, sample_rate)
    if output_ramped is not None:
        write_wav(output_ramped, ramped, sample_rate)

    return {
        "study": "20260828-things-motor-field-probe",
        "decoder": {
            "engine": "ffmpeg",
            "channel_policy": "downmix to mono",
            "sample_format": "float32 during analysis; PCM16 for optional WAV output",
            "sample_rate": sample_rate,
        },
        "inputs": [
            {
                "name": path.name,
                "decoded_frames": frames,
                "trimmed_frames": frame_count,
                "rms": rms(track),
                "peak": peak(track),
            }
            for path, frames, track in zip(paths, decoded_frames, tracks)
        ],
        "render": {
            "mode": mode,
            "speed_hz": speed_hz,
            "phase_at_switch": phase_at_switch,
            "switch_seconds": switch_seconds,
            "switch_frame": switch_frame,
            "ramp_ms": ramp_ms,
            "ramp_frames": ramp_frames,
            "before": [True, True, True, True],
            "after": [True, True, True, False],
        },
        "immediate": immediate_metrics,
        "ramped": ramped_metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tracks", nargs=4, type=Path)
    parser.add_argument("--sample-rate", type=int, default=48_000)
    parser.add_argument("--mode", choices=("skip", "hold", "hole"), default="hold")
    parser.add_argument("--speed-hz", type=float, default=0.5)
    parser.add_argument("--phase-at-switch", type=float, default=0.8)
    parser.add_argument("--switch-seconds", type=float, default=0.2)
    parser.add_argument("--ramp-ms", type=float, default=5.0)
    parser.add_argument("--output-ramped", type=Path)
    parser.add_argument("--output-immediate", type=Path)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            field_probe(
                args.tracks,
                sample_rate=args.sample_rate,
                mode=args.mode,
                speed_hz=args.speed_hz,
                phase_at_switch=args.phase_at_switch,
                switch_seconds=args.switch_seconds,
                ramp_ms=args.ramp_ms,
                output_ramped=args.output_ramped,
                output_immediate=args.output_immediate,
            ),
            ensure_ascii=False,
            indent=None if args.compact else 2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
