#!/usr/bin/env python3
"""Recover voice timing and topology from rendered Hunter v2 WAV files.

The analyzer reads audio only. It does not read the source fixture or answer key.
It is a structural recovery test, not a human listening test.
"""

from __future__ import annotations

import argparse
import json
import math
import wave
from array import array
from pathlib import Path


VOICE_FREQUENCIES = {"bass": 110.0, "chord": 220.0, "melody": 330.0}
GESTURES = {"g1": (0.80, 1.80), "g2": (1.80, 2.80), "g3": (2.80, 4.05)}


def read_mono(path: Path) -> tuple[int, list[float]]:
    with wave.open(str(path), "rb") as source:
        if source.getsampwidth() != 2:
            raise ValueError("expected 16-bit PCM")
        channels = source.getnchannels()
        rate = source.getframerate()
        raw = array("h", source.readframes(source.getnframes()))
    if channels == 1:
        return rate, [value / 32768.0 for value in raw]
    if channels != 2:
        raise ValueError("expected mono or stereo")
    return rate, [(raw[i] + raw[i + 1]) / 65536.0 for i in range(0, len(raw), 2)]


def tone_envelope(samples: list[float], rate: int, frequency: float) -> tuple[list[float], list[float]]:
    window = max(32, round(rate * 0.040))
    hop = max(8, round(rate * 0.005))
    times, amplitudes = [], []
    for start in range(0, max(1, len(samples) - window), hop):
        sin_sum = cos_sum = 0.0
        for offset in range(window):
            phase = 2.0 * math.pi * frequency * offset / rate
            value = samples[start + offset]
            sin_sum += value * math.sin(phase)
            cos_sum += value * math.cos(phase)
        times.append((start + window / 2) / rate)
        amplitudes.append(2.0 * math.hypot(sin_sum, cos_sum) / window)
    return times, amplitudes


def interval_for_voice(times: list[float], amplitudes: list[float], bounds: tuple[float, float]) -> dict:
    indices = [i for i, time in enumerate(times) if bounds[0] <= time <= bounds[1]]
    peak = max(amplitudes[i] for i in indices)
    threshold = max(peak * 0.22, 0.002)
    active = [i for i in indices if amplitudes[i] >= threshold]
    onset = times[min(active)]
    end = times[max(active)]
    return {"onset": round(onset, 3), "duration": round(end - onset, 3)}


def classify(gestures: dict) -> tuple[str, dict]:
    onset_spreads = {}
    duration_spreads = {}
    for name, voices in gestures.items():
        onsets = [item["onset"] for item in voices.values()]
        durations = [item["duration"] for item in voices.values()]
        onset_spreads[name] = round(max(onsets) - min(onsets), 3)
        duration_spreads[name] = round(max(durations) - min(durations), 3)

    if max(onset_spreads.values()) < 0.035 and max(duration_spreads.values()) < 0.055:
        label = "fixed_macro"
    else:
        g3 = gestures["g3"]
        melody_lag = g3["melody"]["onset"] - min(g3["bass"]["onset"], g3["chord"]["onset"])
        melody_extension = g3["melody"]["duration"] - g3["bass"]["duration"]
        label = "hunter_coupling" if melody_lag > 0.020 and melody_extension > 0.20 else "independent_voice"
    return label, {"onset_spread": onset_spreads, "duration_spread": duration_spreads}


def analyze(path: Path) -> dict:
    rate, samples = read_mono(path)
    envelopes = {voice: tone_envelope(samples, rate, frequency) for voice, frequency in VOICE_FREQUENCIES.items()}
    gestures = {}
    for gesture, bounds in GESTURES.items():
        gestures[gesture] = {
            voice: interval_for_voice(times, amplitudes, bounds)
            for voice, (times, amplitudes) in envelopes.items()
        }
    label, features = classify(gestures)
    return {"file": path.name, "estimated_condition": label, "gestures": gestures, **features}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wav", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {
        "schema_version": "sound-lab.synthetic-hunter-audio-recovery/v1",
        "evidence_boundary": "Audio-only structural recovery; not a blind human listening result and not a Charlie Hunter performance measurement.",
        "samples": [analyze(path) for path in args.wav],
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
