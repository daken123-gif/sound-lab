#!/usr/bin/env python3
"""Stress-test Hunter v2 topology recovery under synthetic playback damage.

These transforms are controlled degradations, not measurements of any named
phone, speaker, codec, or listening environment.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import tempfile
import wave
from array import array
from pathlib import Path


ANALYZER_PATH = Path(__file__).with_name("analyze_hunter_stimuli_v2.py")
ANALYZER_SPEC = importlib.util.spec_from_file_location("analyze_hunter_stimuli_v2", ANALYZER_PATH)
analyzer = importlib.util.module_from_spec(ANALYZER_SPEC)
assert ANALYZER_SPEC.loader is not None
ANALYZER_SPEC.loader.exec_module(analyzer)


def read_stereo(path: Path) -> tuple[int, list[float], list[float]]:
    with wave.open(str(path), "rb") as source:
        if (source.getnchannels(), source.getsampwidth()) != (2, 2):
            raise ValueError("expected stereo 16-bit PCM")
        rate = source.getframerate()
        raw = array("h", source.readframes(source.getnframes()))
    return rate, [raw[i] / 32768.0 for i in range(0, len(raw), 2)], [raw[i] / 32768.0 for i in range(1, len(raw), 2)]


def write_stereo(path: Path, rate: int, left: list[float], right: list[float]) -> None:
    packed = array("h")
    for l_value, r_value in zip(left, right):
        packed.append(round(max(-1.0, min(1.0, l_value)) * 32767))
        packed.append(round(max(-1.0, min(1.0, r_value)) * 32767))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(packed.tobytes())


def mono(left: list[float], right: list[float]) -> tuple[list[float], list[float]]:
    mixed = [(l_value + r_value) / 2.0 for l_value, r_value in zip(left, right)]
    return mixed[:], mixed[:]


def highpass(values: list[float], rate: int, cutoff: float, order: int) -> list[float]:
    result = values[:]
    rc = 1.0 / (2.0 * math.pi * cutoff)
    alpha = rc / (rc + 1.0 / rate)
    for _ in range(order):
        filtered = [0.0] * len(result)
        previous_input = result[0]
        previous_output = 0.0
        for index, value in enumerate(result[1:], 1):
            current = alpha * (previous_output + value - previous_input)
            filtered[index] = current
            previous_input, previous_output = value, current
        result = filtered
    return result


def quantize(values: list[float], bits: int) -> list[float]:
    levels = 2 ** bits - 1
    return [round((max(-1.0, min(1.0, value)) + 1.0) * levels / 2.0) * 2.0 / levels - 1.0 for value in values]


def add_noise(left: list[float], right: list[float], snr_db: float, seed: int) -> tuple[list[float], list[float]]:
    energy = sum(value * value for value in left) + sum(value * value for value in right)
    signal_rms = math.sqrt(energy / max(1, len(left) + len(right)))
    noise_rms = signal_rms / (10 ** (snr_db / 20.0))
    rng = random.Random(seed)
    return ([value + rng.gauss(0.0, noise_rms) for value in left], [value + rng.gauss(0.0, noise_rms) for value in right])


def soft_clip(values: list[float], drive: float) -> list[float]:
    scale = math.tanh(drive)
    return [math.tanh(drive * value) / scale for value in values]


def transform(case: str, rate: int, left: list[float], right: list[float], seed: int) -> tuple[list[float], list[float]]:
    if case == "baseline":
        return left, right
    if case == "mono":
        return mono(left, right)
    if case.startswith("quantized_"):
        bits = int(case.removeprefix("quantized_").removesuffix("bit"))
        return quantize(left, bits), quantize(right, bits)
    if case.startswith("noise_"):
        return add_noise(left, right, float(case.split("_")[1].removesuffix("db")), seed)
    if case.startswith("mono_highpass_"):
        mixed_left, mixed_right = mono(left, right)
        cutoff, order = case.removeprefix("mono_highpass_").split("_")
        return highpass(mixed_left, rate, float(cutoff), int(order)), highpass(mixed_right, rate, float(cutoff), int(order))
    if case == "mobile_stress":
        mixed_left, mixed_right = mono(left, right)
        mixed_left = highpass(mixed_left, rate, 180.0, 3)
        mixed_right = highpass(mixed_right, rate, 180.0, 3)
        mixed_left, mixed_right = quantize(mixed_left, 8), quantize(mixed_right, 8)
        mixed_left, mixed_right = soft_clip(mixed_left, 1.5), soft_clip(mixed_right, 1.5)
        return add_noise(mixed_left, mixed_right, 25.0, seed)
    raise ValueError(f"unknown case: {case}")


CASES = [
    "baseline",
    "mono",
    "quantized_8bit",
    "quantized_4bit",
    "noise_30db",
    "noise_20db",
    "noise_10db",
    "noise_0db",
    "mono_highpass_180_2",
    "mono_highpass_260_4",
    "mono_highpass_400_6",
    "mobile_stress",
]


def run(samples: dict[str, Path]) -> dict:
    results = []
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        for case_index, case in enumerate(CASES):
            for sample_id, source in samples.items():
                rate, left, right = read_stereo(source)
                left, right = transform(case, rate, left, right, 20261002 + case_index)
                target = work / f"{case}-{sample_id}.wav"
                write_stereo(target, rate, left, right)
                try:
                    analysis = analyzer.analyze(target)
                    results.append({"case": case, "sample_id": sample_id, "estimated_condition": analysis["estimated_condition"], "status": "recovered"})
                except (ValueError, IndexError) as error:
                    results.append({"case": case, "sample_id": sample_id, "estimated_condition": None, "status": "unresolved", "reason": "voice_activity_below_threshold"})
    return {
        "schema_version": "sound-lab.synthetic-hunter-playback-stress/v1",
        "evidence_boundary": "Synthetic playback degradations only; not a measurement of an iPhone, speaker, codec, room, or human listener.",
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sample_a", type=Path)
    parser.add_argument("sample_b", type=Path)
    parser.add_argument("sample_c", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run({"sample-a": args.sample_a, "sample-b": args.sample_b, "sample-c": args.sample_c})
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
