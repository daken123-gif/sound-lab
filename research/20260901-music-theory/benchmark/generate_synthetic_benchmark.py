#!/usr/bin/env python3
"""Generate controlled audio cases for relational music-analysis tests.

The WAV files are deliberately simple.  Their purpose is not musical realism;
it is to provide exact timing, layer, phase, and transformation ground truth.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 48_000
SEED = 20260901


def empty_audio(seconds: float, channels: int = 2) -> list[list[float]]:
    frames = int(seconds * SAMPLE_RATE)
    return [[0.0] * frames for _ in range(channels)]


def pan_gains(pan: float) -> tuple[float, float]:
    """Equal-power stereo pan, where -1 is left and +1 is right."""
    angle = (max(-1.0, min(1.0, pan)) + 1.0) * math.pi / 4.0
    return math.cos(angle), math.sin(angle)


def add_tone(
    audio: list[list[float]],
    start: float,
    duration: float,
    frequency: float,
    amplitude: float = 0.5,
    pan: float = 0.0,
    waveform: str = "sine",
) -> None:
    first = max(0, int(start * SAMPLE_RATE))
    count = max(1, int(duration * SAMPLE_RATE))
    left_gain, right_gain = pan_gains(pan)
    attack = max(1, int(0.005 * SAMPLE_RATE))
    release = max(1, int(min(0.04, duration / 2.0) * SAMPLE_RATE))

    for offset in range(count):
        frame = first + offset
        if frame >= len(audio[0]):
            break
        phase = 2.0 * math.pi * frequency * offset / SAMPLE_RATE
        if waveform == "saw":
            value = 2.0 * ((frequency * offset / SAMPLE_RATE) % 1.0) - 1.0
        elif waveform == "square":
            value = 1.0 if math.sin(phase) >= 0 else -1.0
        else:
            value = math.sin(phase)

        envelope = min(1.0, offset / attack)
        envelope *= min(1.0, (count - offset) / release)
        sample = value * amplitude * envelope
        audio[0][frame] += sample * left_gain
        audio[1][frame] += sample * right_gain


def add_click(
    audio: list[list[float]],
    time: float,
    amplitude: float = 0.8,
    frequency: float = 1_200.0,
    pan: float = 0.0,
) -> None:
    add_tone(audio, time, 0.035, frequency, amplitude, pan)


def add_noise_tail(
    audio: list[list[float]], start: float, duration: float, amplitude: float = 0.25
) -> None:
    rng = random.Random(SEED + int(start * 1000))
    first = int(start * SAMPLE_RATE)
    count = int(duration * SAMPLE_RATE)
    for offset in range(count):
        frame = first + offset
        if frame >= len(audio[0]):
            break
        decay = math.exp(-5.0 * offset / max(1, count))
        value = rng.uniform(-1.0, 1.0) * amplitude * decay
        audio[0][frame] += value * 0.8
        audio[1][frame] += value


def write_wav(path: Path, audio: list[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max(max(abs(value) for value in channel) for channel in audio)
    scale = 0.92 / peak if peak > 0.92 else 1.0
    interleaved = bytearray()
    for frame in range(len(audio[0])):
        for channel in audio:
            value = max(-1.0, min(1.0, channel[frame] * scale))
            interleaved.extend(struct.pack("<h", round(value * 32767)))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(len(audio))
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(interleaved)


def case_s01() -> tuple[list[list[float]], dict]:
    audio = empty_audio(10.0)
    events = []
    for index in range(18):
        time = 0.5 + index * 0.5
        accent = 1.0 if index % 2 == 0 else 0.55
        add_click(audio, time, 0.72 * accent, 1_000 if index % 2 == 0 else 700)
        events.append({"time": time, "accent": accent})
    truth = {
        "id": "S01",
        "target": "half_double_tempo_ambiguity",
        "events": events,
        "accepted_meter_hypotheses": [
            {"bpm": 120, "beat_period": 0.5, "phase": 0.5},
            {"bpm": 60, "beat_period": 1.0, "phase": 0.5},
        ],
        "must_not": ["collapse_to_single_tempo_without_uncertainty"],
    }
    return audio, truth


def case_s02() -> tuple[list[list[float]], dict]:
    audio = empty_audio(10.0)
    phase = 0.75
    period = 2.0
    events = []
    for cycle in range(5):
        for step, frequency in enumerate((180, 900, 450, 900)):
            time = phase + cycle * period + step * 0.5
            if time < 10.0:
                add_click(audio, time, 0.7 if step == 0 else 0.45, frequency)
                events.append({"time": time, "cycle": cycle, "step": step})
    return audio, {
        "id": "S02",
        "target": "cycle_phase_separation",
        "events": events,
        "cycle": {"period": period, "phase": phase},
        "must_not": ["assume_file_start_is_cycle_origin"],
    }


def case_s03() -> tuple[list[list[float]], dict]:
    audio = empty_audio(10.0)
    subdivision = 0.25
    layers = {"three": [], "four": []}
    for step in range(1, 40):
        time = step * subdivision
        if step % 3 == 0:
            add_click(audio, time, 0.5, 330, -0.65)
            layers["three"].append(time)
        if step % 4 == 0:
            add_click(audio, time, 0.5, 660, 0.65)
            layers["four"].append(time)
    return audio, {
        "id": "S03",
        "target": "polymetric_layer_hypotheses",
        "layers": layers,
        "subdivision": subdivision,
        "periods": {"three": 0.75, "four": 1.0, "joint": 3.0},
    }


def case_s04() -> tuple[list[list[float]], dict]:
    audio = empty_audio(12.0)
    beats = []
    time = 0.5
    index = 0
    offsets = (-0.018, 0.012, -0.006, 0.021)
    while time < 11.5:
        progress = min(1.0, time / 11.5)
        interval = 0.60 + (0.45 - 0.60) * progress
        residual = offsets[index % len(offsets)]
        add_click(audio, time, 0.7, 220)
        add_click(audio, time + residual, 0.4, 1_200)
        beats.append(
            {
                "grid_time": round(time, 6),
                "secondary_time": round(time + residual, 6),
                "micro_residual": residual,
                "local_period": round(interval, 6),
            }
        )
        time += interval
        index += 1
    return audio, {
        "id": "S04",
        "target": "tempo_curve_microtiming_separation",
        "beats": beats,
        "tempo_curve_bpm": {"start": 100.0, "end": 133.333333},
    }


def case_s05() -> tuple[list[list[float]], dict]:
    audio = empty_audio(12.0)
    sections = []
    patterns = {
        "quantized": (0.0, 0.0, 0.0, 0.0),
        "natural": (-0.012, 0.018, -0.006, 0.014),
        "expanded": (-0.036, 0.054, -0.018, 0.042),
    }
    for section_index, (name, offsets) in enumerate(patterns.items()):
        start = section_index * 4.0
        event_rows = []
        for step in range(8):
            grid = start + 0.25 + step * 0.45
            residual = offsets[step % 4]
            add_click(audio, grid + residual, 0.65, 520)
            event_rows.append({"grid": grid, "residual": residual})
        sections.append({"name": name, "range": [start, start + 4.0], "events": event_rows})
    return audio, {
        "id": "S05",
        "target": "microtiming_not_scalar_groove",
        "sections": sections,
        "must_not": ["rank_groove_by_absolute_timing_deviation_only"],
    }


def case_s06() -> tuple[list[list[float]], dict]:
    audio = empty_audio(10.0)
    events = []
    for index in range(19):
        time = 0.5 + index * 0.5
        waveform = "sine" if time < 5.0 else "saw"
        add_tone(audio, time, 0.12, 440, 0.45, waveform=waveform)
        events.append({"time": time, "waveform": waveform})
    return audio, {
        "id": "S06",
        "target": "channel_specific_boundary",
        "events": events,
        "boundaries": [{"time": 5.0, "channel": "timbre"}],
        "invariants": ["pitch", "rhythm", "dynamics"],
    }


def case_s07() -> tuple[list[list[float]], dict]:
    audio = empty_audio(10.0)
    relations = []
    for index in range(18):
        time = 0.5 + index * 0.5
        anchor = "low" if time < 5.0 else "high"
        add_click(audio, time, 0.7, 180 if anchor == "low" else 1_000)
        offbeat_layer = "high" if anchor == "low" else "low"
        add_click(audio, time + 0.25, 0.35, 1_000 if offbeat_layer == "high" else 180)
        relations.append({"time": time, "pulse_anchor_layer": anchor})
    return audio, {
        "id": "S07",
        "target": "role_transfer_between_layers",
        "relations": relations,
        "boundary": {"time": 5.0, "type": "role_transfer"},
    }


def case_s08() -> tuple[list[list[float]], dict]:
    audio = empty_audio(10.0)
    direct_events = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    for time in direct_events:
        add_click(audio, time, 0.7, 700)
    add_noise_tail(audio, 3.0, 4.0)
    return audio, {
        "id": "S08",
        "target": "direct_sound_reverb_tail_separation",
        "direct_events": direct_events,
        "boundaries": [
            {"time": 3.035, "type": "direct_sound_end"},
            {"range": [6.5, 7.0], "type": "perceptual_tail_end"},
        ],
    }


def case_s09() -> tuple[list[list[float]], dict]:
    audio = empty_audio(10.0)
    events = []
    for index in range(18):
        time = 0.5 + index * 0.5
        pan = -0.9 if index % 2 == 0 else 0.9
        add_click(audio, time, 0.6, 600, pan)
        events.append({"time": time, "pan": pan})
    return audio, {
        "id": "S09",
        "target": "spatial_periodicity",
        "events": events,
        "periods": {"onset": 0.5, "stereo_cycle": 1.0},
        "must_not": ["discard_stereo_before_spatial_analysis"],
    }


def case_s10() -> tuple[list[list[float]], dict]:
    audio = empty_audio(10.0)
    cycles = []
    amplitudes = (0.28, 0.50, 0.76, 0.40)
    for cycle, amplitude in enumerate(amplitudes):
        start = 0.5 + cycle * 2.0
        events = []
        for step in range(4):
            time = start + step * 0.5
            add_click(audio, time, amplitude, 500)
            events.append({"time": time, "amplitude": amplitude})
        cycles.append({"cycle": cycle, "events": events})
    return audio, {
        "id": "S10",
        "target": "repetition_with_dynamics_transformation",
        "cycle_period": 2.0,
        "cycles": cycles,
        "invariants": ["onset_pattern", "pitch", "timbre"],
    }


def case_s11() -> tuple[list[list[float]], dict]:
    audio = empty_audio(12.0)
    periods = (1.80, 1.95, 2.10, 2.25, 2.40)
    cycles = []
    start = 0.4
    for index, period in enumerate(periods):
        event_times = []
        for step in range(4):
            time = start + step * period / 4.0
            add_click(audio, time, 0.65 if step == 0 else 0.38, 300 + step * 170)
            event_times.append(time)
        cycles.append({"index": index, "start": start, "period": period, "events": event_times})
        start += period
    return audio, {
        "id": "S11",
        "target": "cycle_period_drift",
        "cycles": cycles,
        "must_not": ["force_all_cycles_to_median_period"],
    }


def case_s12() -> tuple[list[list[float]], dict]:
    audio = empty_audio(10.0)
    kick_events = []
    bass_events = []
    for index in range(18):
        time = 0.5 + index * 0.5
        add_tone(audio, time, 0.22, 62, 0.58, waveform="sine")
        kick_events.append(time)
        bass_time = time + (0.0 if index % 4 == 0 else 0.12)
        add_tone(audio, bass_time, 0.36, 66, 0.48, waveform="saw")
        bass_events.append(bass_time)
    return audio, {
        "id": "S12",
        "target": "source_overlap_and_role_uncertainty",
        "layers": {"kick": kick_events, "bass": bass_events},
        "overlap_region_hz": [55, 140],
        "must_not": ["treat_separated_stems_as_observed_ground_truth"],
    }


CASES = (
    case_s01,
    case_s02,
    case_s03,
    case_s04,
    case_s05,
    case_s06,
    case_s07,
    case_s08,
    case_s09,
    case_s10,
    case_s11,
    case_s12,
)


def generate(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "benchmark": "music-theory-relational-synthetic-v0.1",
        "sample_rate": SAMPLE_RATE,
        "seed": SEED,
        "cases": [],
    }
    for build_case in CASES:
        audio, truth = build_case()
        filename = f"{truth['id'].lower()}.wav"
        write_wav(output_dir / filename, audio)
        truth["audio"] = {
            "file": filename,
            "channels": len(audio),
            "frames": len(audio[0]),
            "duration": len(audio[0]) / SAMPLE_RATE,
        }
        manifest["cases"].append(truth)

    manifest_path = output_dir / "ground-truth.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("generated"),
        help="Directory for generated WAV files and ground-truth.json",
    )
    args = parser.parse_args()
    print(generate(args.output))


if __name__ == "__main__":
    main()
