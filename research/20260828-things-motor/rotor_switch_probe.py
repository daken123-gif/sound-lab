#!/usr/bin/env python3
"""Measure participation switching while the Rotor phase keeps moving."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from rotor_audio_probe import material_cases, peak, rms, write_wav
from rotor_layout import layout_coefficients


def render_switch(
    tracks: list[list[float]],
    *,
    sample_rate: int,
    mode: str,
    switch_frame: int,
    phase_at_switch: float,
    speed_hz: float,
    transition_frames: int,
    before: list[bool] | None = None,
    after: list[bool] | None = None,
) -> tuple[list[float], list[list[float]]]:
    """Render a state change without stopping or resetting rotor phase.

    During a transition, both the old and new layouts are recalculated from the
    moving phase every sample, then blended. The ramp therefore changes only the
    layout delta: an unaffected arc keeps its normal motion, and the final sample
    reaches the live destination rather than a stale captured target.
    """
    if len(tracks) != 4 or len({len(track) for track in tracks}) != 1:
        raise ValueError("render_switch expects four equal-length tracks")
    if transition_frames < 1:
        raise ValueError("transition_frames must be positive")
    frame_count = len(tracks[0])
    if not 1 <= switch_frame < frame_count:
        raise ValueError("switch_frame must be inside the rendered range")
    before = before or [True, True, True, True]
    after = after or [True, True, True, False]

    output: list[float] = []
    history: list[list[float]] = []
    for frame in range(frame_count):
        phase = (phase_at_switch + (frame - switch_frame) * speed_hz / sample_rate) % 1.0
        active = before if frame < switch_frame else after
        target = layout_coefficients(phase, active, mode)
        if switch_frame <= frame < switch_frame + transition_frames:
            progress = (frame - switch_frame + 1) / transition_frames
            old_layout = layout_coefficients(phase, before, mode)
            new_layout = layout_coefficients(phase, after, mode)
            coefficients = [
                old + (new - old) * progress
                for old, new in zip(old_layout, new_layout)
            ]
        else:
            coefficients = target
        history.append(coefficients)
        output.append(sum(coefficients[index] * tracks[index][frame] for index in range(4)))
    return output, history


def _max_coefficient_step(
    history: list[list[float]], start: int, stop: int
) -> float:
    return max(
        abs(current - previous)
        for frame in range(max(1, start), min(len(history), stop))
        for previous, current in zip(history[frame - 1], history[frame])
    )


def scenario_metrics(
    tracks: list[list[float]],
    *,
    sample_rate: int,
    mode: str,
    switch_frame: int,
    phase_at_switch: float,
    speed_hz: float,
    transition_frames: int,
) -> tuple[dict[str, float | int | str], list[float]]:
    output, history = render_switch(
        tracks,
        sample_rate=sample_rate,
        mode=mode,
        switch_frame=switch_frame,
        phase_at_switch=phase_at_switch,
        speed_hz=speed_hz,
        transition_frames=transition_frames,
    )
    window_stop = switch_frame + transition_frames + 1
    window = output[max(0, switch_frame - 1) : min(len(output), window_stop)]
    return (
        {
            "mode": mode,
            "transition_frames": transition_frames,
            "coefficient_step_at_switch": max(
                abs(a - b)
                for a, b in zip(history[switch_frame - 1], history[switch_frame])
            ),
            "maximum_coefficient_step_during_transition": _max_coefficient_step(
                history, switch_frame, window_stop
            ),
            "transition_window_rms": rms(window),
            "transition_window_peak": peak(window),
            "whole_render_peak": peak(output),
        },
        output,
    )


def probe(
    sample_rate: int = 48_000,
    seconds: float = 1.0,
    speed_hz: float = 0.5,
    ramp_frames: int = 240,
    wav_dir: Path | None = None,
) -> dict[str, object]:
    tracks = material_cases(sample_rate, seconds)["unrelated"]
    switch_frame = round(0.2 * sample_rate)
    scenarios = {
        "nonlocal_phase_0_10": 0.10,
        "audible_track4_phase_0_80": 0.80,
    }
    report: dict[str, object] = {
        "sample_rate": sample_rate,
        "seconds": seconds,
        "speed_hz": speed_hz,
        "switch_frame": switch_frame,
        "before": [True, True, True, True],
        "after": [True, True, True, False],
        "scenarios": {},
    }
    for scenario, phase in scenarios.items():
        scenario_report: dict[str, object] = {}
        for mode in ("skip", "hold", "hole"):
            mode_report: dict[str, object] = {}
            for label, frames in (("immediate", 1), ("ramp_5ms", ramp_frames)):
                metrics, output = scenario_metrics(
                    tracks,
                    sample_rate=sample_rate,
                    mode=mode,
                    switch_frame=switch_frame,
                    phase_at_switch=phase,
                    speed_hz=speed_hz,
                    transition_frames=frames,
                )
                mode_report[label] = metrics
                if wav_dir is not None:
                    write_wav(
                        wav_dir / f"{scenario}--{mode}--{label}.wav",
                        output,
                        sample_rate,
                    )
            scenario_report[mode] = mode_report
        report["scenarios"][scenario] = scenario_report
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
