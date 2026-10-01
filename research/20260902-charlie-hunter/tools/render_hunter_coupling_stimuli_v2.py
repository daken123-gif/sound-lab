#!/usr/bin/env python3
"""Render energy-matched blind synthetic Hunter-coupling stimuli.

The renderer uses elementary sine tones only. It tests whether causal topology
can remain audible after note count, aggregate note duration, global RMS, and
peak are controlled. It does not model or imitate Charlie Hunter's sound.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "data" / "synthetic-hunter-coupling-v2.json"
DEFAULT_OUTPUT = ROOT / "data" / "synthetic-hunter-listening-v2"
SAMPLE_RATE = 22_050
CHANNELS = 2
SAMPLE_WIDTH = 2
DURATION_SECONDS = 4.25
TARGET_TONE_RMS = 10 ** (-21.0 / 20.0)
CALIBRATION_PEAK = 0.55
VOICE = {
    "bass": {"frequency_hz": 110.0, "pan": 0.0},
    "chord": {"frequency_hz": 220.0, "pan": -0.5},
    "melody": {"frequency_hz": 330.0, "pan": 0.5},
}
BLIND_ORDER = {
    "sample-a.wav": "fixed_macro",
    "sample-b.wav": "hunter_coupling",
    "sample-c.wav": "independent_voice",
}
WINDOWS = {
    "g1": (0.80, 1.80),
    "g2": (1.80, 2.80),
    "g3": (2.80, 4.00),
}


def envelope(position: float, duration: float) -> float:
    attack = min(0.012, duration / 4)
    release = min(0.040, duration / 3)
    if position < 0 or position >= duration:
        return 0.0
    if position < attack:
        return position / attack
    if position > duration - release:
        return max(0.0, (duration - position) / release)
    return 1.0


def constant_power_pan(pan: float) -> tuple[float, float]:
    angle = (pan + 1.0) * math.pi / 4.0
    return math.cos(angle), math.sin(angle)


def add_tone(left: list[float], right: list[float], slot: dict) -> None:
    if not slot["active"]:
        return
    spec = VOICE[slot["voice"]]
    l_pan, r_pan = constant_power_pan(spec["pan"])
    start = round(slot["onset"] * SAMPLE_RATE)
    count = round(slot["duration"] * SAMPLE_RATE)
    for offset in range(count):
        index = start + offset
        if index >= len(left):
            break
        position = offset / SAMPLE_RATE
        value = math.sin(2 * math.pi * spec["frequency_hz"] * position)
        value *= envelope(position, slot["duration"])
        left[index] += value * l_pan
        right[index] += value * r_pan


def add_gesture_markers(left: list[float], right: list[float]) -> None:
    duration = 0.012
    for onset in (1.0, 2.0, 3.0):
        start = round(onset * SAMPLE_RATE)
        count = round(duration * SAMPLE_RATE)
        for offset in range(count):
            position = offset / SAMPLE_RATE
            value = math.sin(2 * math.pi * 1320.0 * position)
            value *= envelope(position, duration) * 0.018
            left[start + offset] += value
            right[start + offset] += value


def stereo_rms(left: list[float], right: list[float], start: int = 0, end: int | None = None) -> float:
    end = len(left) if end is None else end
    count = max(1, 2 * (end - start))
    energy = sum(v * v for v in left[start:end]) + sum(v * v for v in right[start:end])
    return math.sqrt(energy / count)


def add_calibration_pulse(left: list[float], right: list[float]) -> None:
    duration = 0.012
    start = round(0.25 * SAMPLE_RATE)
    count = round(duration * SAMPLE_RATE)
    for offset in range(count):
        position = offset / SAMPLE_RATE
        value = math.sin(2 * math.pi * 880.0 * position)
        value *= envelope(position, duration) * CALIBRATION_PEAK
        left[start + offset] += value
        right[start + offset] += value


def render_float(condition: dict) -> tuple[list[float], list[float], float]:
    frame_count = round(DURATION_SECONDS * SAMPLE_RATE)
    left = [0.0] * frame_count
    right = [0.0] * frame_count
    add_gesture_markers(left, right)
    for slot in condition["slots"]:
        add_tone(left, right, slot)
    raw_rms = stereo_rms(left, right)
    scale = TARGET_TONE_RMS / raw_rms
    left = [value * scale for value in left]
    right = [value * scale for value in right]
    add_calibration_pulse(left, right)
    return left, right, scale


def metrics(left: list[float], right: list[float], condition: dict, scale: float) -> dict:
    peak = max(max(abs(v) for v in left), max(abs(v) for v in right))
    rms = stereo_rms(left, right)
    windows = {}
    for name, (start_s, end_s) in WINDOWS.items():
        start = round(start_s * SAMPLE_RATE)
        end = round(end_s * SAMPLE_RATE)
        value = stereo_rms(left, right, start, end)
        windows[name] = round(20 * math.log10(max(value, 1e-12)), 6)
    duration_by_gesture = {}
    for gesture in WINDOWS:
        duration_by_gesture[gesture] = round(sum(
            slot["duration"] for slot in condition["slots"]
            if slot["gesture_id"] == gesture and slot["active"]
        ), 6)
    return {
        "active_note_count": sum(1 for slot in condition["slots"] if slot["active"]),
        "duration_sum_seconds": duration_by_gesture,
        "global_rms_dbfs": round(20 * math.log10(max(rms, 1e-12)), 6),
        "interval_rms_dbfs": windows,
        "normalization_scale": round(scale, 9),
        "peak": round(peak, 6),
    }


def pcm_bytes(left: list[float], right: list[float]) -> bytes:
    frames = bytearray()
    for l_value, r_value in zip(left, right):
        l_pcm = round(max(-1.0, min(1.0, l_value)) * 32767)
        r_pcm = round(max(-1.0, min(1.0, r_value)) * 32767)
        frames.extend(struct.pack("<hh", l_pcm, r_pcm))
    return bytes(frames)


def write_wav(path: Path, pcm: bytes) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(CHANNELS)
        output.setsampwidth(SAMPLE_WIDTH)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(pcm)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(fixture_path: Path, output_dir: Path) -> tuple[dict, dict]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    samples = []
    for filename, condition_name in BLIND_ORDER.items():
        condition = fixture["conditions"][condition_name]
        left, right, scale = render_float(condition)
        path = output_dir / filename
        write_wav(path, pcm_bytes(left, right))
        item_metrics = metrics(left, right, condition, scale)
        samples.append({
            "sample_id": filename.removesuffix(".wav"),
            "file": filename,
            "sha256": sha256(path),
            "frames": round(DURATION_SECONDS * SAMPLE_RATE),
            **item_metrics,
        })
    manifest = {
        "schema_version": "sound-lab.synthetic-hunter-listening/v2",
        "evidence_boundary": "Energy-matched synthetic topology comparison; no Charlie Hunter recording or performance measurement is used.",
        "sample_rate": SAMPLE_RATE,
        "channels": CHANNELS,
        "sample_width_bytes": SAMPLE_WIDTH,
        "duration_seconds": DURATION_SECONDS,
        "gesture_markers_seconds": [1.0, 2.0, 3.0],
        "calibration_pulse_seconds": 0.25,
        "matching_method": "Equal active-note count and per-gesture duration sums, constant-power panning, then one global RMS scalar per complete tone stimulus. An identical isolated pulse fixes peak.",
        "samples": samples,
    }
    answer_key = {
        "schema_version": "sound-lab.synthetic-hunter-listening-key/v2",
        "mapping": {filename.removesuffix(".wav"): condition for filename, condition in BLIND_ORDER.items()},
        "use_after_scoring": True,
        "source_fixture": "../synthetic-hunter-coupling-v2.json",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "answer-key.json").write_text(json.dumps(answer_key, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest, answer_key


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest, _ = render(args.fixture, args.output_dir)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
