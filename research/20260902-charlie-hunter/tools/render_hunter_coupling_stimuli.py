#!/usr/bin/env python3
"""Render blind synthetic listening stimuli for Hunter coupling research.

Only elementary sine tones and identical gesture markers are synthesized.
The source fixture contains synthetic topology contrasts, not measurements of
Charlie Hunter or an attempt to imitate his sound.
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
DEFAULT_FIXTURE = ROOT / "data" / "synthetic-hunter-coupling-v1.json"
DEFAULT_OUTPUT = ROOT / "data" / "synthetic-hunter-listening-v1"
SAMPLE_RATE = 22_050
CHANNELS = 2
SAMPLE_WIDTH = 2
DURATION_SECONDS = 4.25
VOICE = {
    "bass": {"frequency_hz": 110.0, "gain": 0.22, "pan": 0.0},
    "chord": {"frequency_hz": 220.0, "gain": 0.18, "pan": -0.35},
    "melody": {"frequency_hz": 330.0, "gain": 0.14, "pan": 0.35},
}
BLIND_ORDER = {
    "sample-a.wav": "hunter_coupling",
    "sample-b.wav": "independent_voice",
    "sample-c.wav": "fixed_macro",
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


def add_tone(left: list[float], right: list[float], slot: dict) -> None:
    if not slot["active"]:
        return
    spec = VOICE[slot["voice"]]
    start = max(0, round(slot["onset"] * SAMPLE_RATE))
    count = max(1, round(slot["duration"] * SAMPLE_RATE))
    left_gain = spec["gain"] * (1.0 - max(0.0, spec["pan"]))
    right_gain = spec["gain"] * (1.0 + min(0.0, spec["pan"]))
    for offset in range(count):
        index = start + offset
        if index >= len(left):
            break
        position = offset / SAMPLE_RATE
        value = (
            math.sin(2.0 * math.pi * spec["frequency_hz"] * position)
            * envelope(position, slot["duration"])
        )
        left[index] += value * left_gain
        right[index] += value * right_gain


def add_gesture_markers(left: list[float], right: list[float]) -> None:
    """Add the same quiet 18 ms marker at 1, 2, and 3 seconds."""
    duration = 0.018
    gain = 0.055
    for onset in (1.0, 2.0, 3.0):
        start = round(onset * SAMPLE_RATE)
        count = round(duration * SAMPLE_RATE)
        for offset in range(count):
            index = start + offset
            position = offset / SAMPLE_RATE
            value = (
                math.sin(2.0 * math.pi * 1320.0 * position)
                * envelope(position, duration)
                * gain
            )
            left[index] += value
            right[index] += value


def pcm_bytes(condition: dict) -> tuple[bytes, float]:
    frame_count = round(DURATION_SECONDS * SAMPLE_RATE)
    left = [0.0] * frame_count
    right = [0.0] * frame_count
    add_gesture_markers(left, right)
    for slot in condition["slots"]:
        add_tone(left, right, slot)
    peak = max(max(abs(v) for v in left), max(abs(v) for v in right))
    scale = 0.92 / peak if peak > 0.92 else 1.0
    frames = bytearray()
    for l_value, r_value in zip(left, right):
        l_pcm = round(max(-1.0, min(1.0, l_value * scale)) * 32767)
        r_pcm = round(max(-1.0, min(1.0, r_value * scale)) * 32767)
        frames.extend(struct.pack("<hh", l_pcm, r_pcm))
    return bytes(frames), min(peak * scale, 1.0)


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
        pcm, peak = pcm_bytes(fixture["conditions"][condition_name])
        path = output_dir / filename
        write_wav(path, pcm)
        samples.append(
            {
                "sample_id": filename.removesuffix(".wav"),
                "file": filename,
                "sha256": sha256(path),
                "frames": round(DURATION_SECONDS * SAMPLE_RATE),
                "peak": round(peak, 6),
            }
        )
    manifest = {
        "schema_version": "sound-lab.synthetic-hunter-listening/v1",
        "evidence_boundary": (
            "Blind synthetic tone comparison only; condition names are omitted "
            "from this manifest and no Charlie Hunter recording is used."
        ),
        "sample_rate": SAMPLE_RATE,
        "channels": CHANNELS,
        "sample_width_bytes": SAMPLE_WIDTH,
        "duration_seconds": DURATION_SECONDS,
        "gesture_markers_seconds": [1.0, 2.0, 3.0],
        "voice_frequencies_hz": {
            name: spec["frequency_hz"] for name, spec in VOICE.items()
        },
        "samples": samples,
    }
    answer_key = {
        "schema_version": "sound-lab.synthetic-hunter-listening-key/v1",
        "mapping": {
            filename.removesuffix(".wav"): condition
            for filename, condition in BLIND_ORDER.items()
        },
        "use_after_scoring": True,
        "source_fixture": "../synthetic-hunter-coupling-v1.json",
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "answer-key.json").write_text(
        json.dumps(answer_key, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
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
