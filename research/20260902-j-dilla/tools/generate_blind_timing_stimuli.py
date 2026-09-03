#!/usr/bin/env python3
"""Generate anonymous synthetic WAVs for a timing-relation listening test.

No J Dilla recording, sample, MIDI, or measured onset is used.  The two
conditions contain the same synthetic voices and event counts; only event
timing differs.  The condition key is written separately from the public
listening manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import struct
import wave
from pathlib import Path
from typing import Any


SAMPLE_RATE = 44_100
SUBDIVISION_SECONDS = 0.125
PATTERN_STEPS = 8
CYCLES = 8
LEAD_IN_SECONDS = 0.25
TAIL_SECONDS = 0.25
TARGET_RMS = 0.04

VOICE_STEPS = {
    "kick": (0, 3, 4, 6),
    "snare": (2, 6),
    "hat": tuple(range(PATTERN_STEPS)),
}

VOICE_SHAPES = {
    "kick": (0.000, -0.012, 0.006, -0.004),
    "snare": (0.000, 0.018, 0.004, 0.011),
    "hat": (-0.006, 0.009, -0.003, 0.014),
}

VOICE_TONES = {
    "kick": (70.0, 0.080, 0.80),
    "snare": (240.0, 0.050, 0.55),
    "hat": (1800.0, 0.020, 0.25),
}


def global_swing_offset(step: int) -> float:
    return 0.020 if step % 2 else 0.0


def structured_offset(voice: str, step: int) -> float:
    return VOICE_SHAPES[voice][step % len(VOICE_SHAPES[voice])]


def event_offset(condition: str, voice: str, step: int) -> float:
    if condition == "global_swing":
        return global_swing_offset(step)
    if condition == "structured_relation":
        return structured_offset(voice, step)
    raise ValueError(f"unknown condition: {condition}")


def pulse(voice: str) -> list[float]:
    frequency, duration, amplitude = VOICE_TONES[voice]
    length = int(round(duration * SAMPLE_RATE))
    values = []
    for index in range(length):
        time = index / SAMPLE_RATE
        envelope = math.exp(-7.0 * index / max(1, length - 1))
        values.append(amplitude * envelope * math.sin(2.0 * math.pi * frequency * time))
    return values


def render(condition: str) -> list[float]:
    pattern_seconds = PATTERN_STEPS * SUBDIVISION_SECONDS
    duration = LEAD_IN_SECONDS + CYCLES * pattern_seconds + TAIL_SECONDS
    audio = [0.0] * int(round(duration * SAMPLE_RATE))
    pulses = {voice: pulse(voice) for voice in VOICE_STEPS}

    for cycle in range(CYCLES):
        cycle_start = LEAD_IN_SECONDS + cycle * pattern_seconds
        for voice, steps in VOICE_STEPS.items():
            source = pulses[voice]
            for step in steps:
                onset = cycle_start + step * SUBDIVISION_SECONDS + event_offset(condition, voice, step)
                start = int(round(onset * SAMPLE_RATE))
                for offset, sample in enumerate(source):
                    target = start + offset
                    if 0 <= target < len(audio):
                        audio[target] += sample

    rms = math.sqrt(sum(sample * sample for sample in audio) / len(audio))
    if rms == 0.0:
        raise ValueError("rendered silence")
    scale = TARGET_RMS / rms
    peak = max(abs(sample * scale) for sample in audio)
    if peak > 0.95:
        scale *= 0.95 / peak
    return [sample * scale for sample in audio]


def pcm16(audio: list[float]) -> bytes:
    return b"".join(
        struct.pack("<h", max(-32768, min(32767, int(round(sample * 32767.0)))))
        for sample in audio
    )


def write_wav(path: Path, audio: list[float]) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm16(audio))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pcm_rms(audio: list[float]) -> float:
    return math.sqrt(sum(sample * sample for sample in audio) / len(audio))


def generate_pack(output: Path, seed: int = 20260903) -> tuple[dict[str, Any], dict[str, Any]]:
    output.mkdir(parents=True, exist_ok=True)
    conditions = ["global_swing", "structured_relation"]
    labels = ["stimulus-A.wav", "stimulus-B.wav"]
    random.Random(seed).shuffle(labels)
    assignment = dict(zip(conditions, labels))

    rendered = {condition: render(condition) for condition in conditions}
    file_entries = []
    for condition in conditions:
        filename = assignment[condition]
        path = output / filename
        write_wav(path, rendered[condition])
        file_entries.append(
            {
                "stimulus_id": path.stem,
                "filename": filename,
                "sha256": sha256_file(path),
                "duration_seconds": len(rendered[condition]) / SAMPLE_RATE,
                "sample_rate_hz": SAMPLE_RATE,
                "channels": 1,
                "pcm_bits": 16,
                "rms_before_pcm_quantization": round(pcm_rms(rendered[condition]), 9),
            }
        )
    file_entries.sort(key=lambda item: item["filename"])

    manifest = {
        "schema_version": "sound-lab.j-dilla.blind-timing-stimuli/v1",
        "scope": "anonymous synthetic listening stimuli; no artist audio or measured artist timing",
        "files": file_entries,
        "shared_content": {
            "voice_steps": {key: list(value) for key, value in VOICE_STEPS.items()},
            "voice_tones": {key: list(value) for key, value in VOICE_TONES.items()},
            "cycles": CYCLES,
            "subdivision_seconds": SUBDIVISION_SECONDS,
            "lead_in_seconds": LEAD_IN_SECONDS,
            "tail_seconds": TAIL_SECONDS,
        },
        "instructions": [
            "play both files at the same device volume",
            "do not inspect condition-key.json before locking responses",
            "rate continuity, forward motion, instability, human intention and preference",
            "do not rate Dilla likeness because these are synthetic counterexamples",
        ],
    }
    key = {
        "schema_version": "sound-lab.j-dilla.blind-timing-key/v1",
        "seed": seed,
        "condition_to_file": assignment,
        "disclosure_rule": "open only after the listener response has been locked",
    }
    (output / "blind-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "condition-key.json").write_text(
        json.dumps(key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest, key


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--seed", type=int, default=20260903)
    args = parser.parse_args()
    manifest, _ = generate_pack(args.output, args.seed)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
