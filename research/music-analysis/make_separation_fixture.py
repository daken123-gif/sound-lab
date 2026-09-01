#!/usr/bin/env python3
"""Create a deterministic, known-stem fixture for separator sanity checks.

This is deliberately not a realism benchmark.  It only tests whether a chosen
separator is directionally responsive to drum-like and bass-like content before
we allow it to influence claims about commercial recordings.
"""

from pathlib import Path

import numpy as np
import soundfile as sf


SR = 44_100
DURATION = 30.0
OUT = Path(__file__).with_name("fixture")
RNG = np.random.default_rng(20260901)


def exp_env(length: int, decay_seconds: float) -> np.ndarray:
    return np.exp(-np.arange(length) / (SR * decay_seconds))


def add_at(dst: np.ndarray, start: int, src: np.ndarray) -> None:
    stop = min(len(dst), start + len(src))
    if stop > start:
        dst[start:stop] += src[: stop - start]


def make_drums(n: int) -> np.ndarray:
    mono = np.zeros(n, dtype=np.float64)
    beat = 60.0 / 112.0
    bars = int(DURATION / (beat * 4)) + 1
    for bar in range(bars):
        base = bar * 4 * beat
        # Kick on 1 and 3, plus a quiet displaced kick every second bar.
        for pos, gain in [(0.0, 0.95), (2.0, 0.78)]:
            start = int((base + pos * beat) * SR)
            length = int(0.42 * SR)
            t = np.arange(length) / SR
            phase = 2 * np.pi * (82 * t - 52 * t * t)
            kick = gain * np.sin(phase) * exp_env(length, 0.11)
            add_at(mono, start, kick)
        if bar % 2:
            start = int((base + 2.72 * beat) * SR)
            length = int(0.28 * SR)
            t = np.arange(length) / SR
            kick = 0.38 * np.sin(2 * np.pi * (76 * t - 42 * t * t)) * exp_env(length, 0.085)
            add_at(mono, start, kick)

        # Snare/backbeat on 2 and 4.
        for pos in (1.0, 3.0):
            start = int((base + pos * beat) * SR)
            length = int(0.24 * SR)
            t = np.arange(length) / SR
            noise = RNG.normal(0, 1, length)
            tone = np.sin(2 * np.pi * 185 * t)
            snare = (0.55 * noise + 0.25 * tone) * exp_env(length, 0.055)
            add_at(mono, start, snare)

        # Eighth-note hats with alternating intensity.
        for eighth in range(8):
            start = int((base + eighth * beat / 2) * SR)
            length = int(0.075 * SR)
            noise = RNG.normal(0, 1, length)
            # First difference is a cheap deterministic high-pass.
            hat = np.diff(np.r_[0.0, noise]) * exp_env(length, 0.018)
            add_at(mono, start, (0.10 if eighth % 2 else 0.16) * hat)

    mono = np.tanh(mono * 0.9)
    # Tiny stereo offset prevents a purely mono fixture.
    return np.stack([mono, np.roll(mono, 11) * 0.97], axis=1)


def make_bass(n: int) -> np.ndarray:
    t = np.arange(n) / SR
    beat = 60.0 / 112.0
    notes = [55.0, 55.0, 65.406, 73.416, 49.0, 55.0, 41.203, 49.0]
    mono = np.zeros(n, dtype=np.float64)
    for idx in range(int(DURATION / (beat / 2)) + 1):
        start = int(idx * beat / 2 * SR)
        length = int(0.46 * beat * SR)
        tt = np.arange(length) / SR
        freq = notes[idx % len(notes)]
        wave = np.sin(2 * np.pi * freq * tt) + 0.28 * np.sin(4 * np.pi * freq * tt)
        env = np.minimum(1.0, tt / 0.008) * np.exp(-tt / 0.23)
        add_at(mono, start, 0.42 * wave * env)
    wobble = 0.94 + 0.06 * np.sin(2 * np.pi * 0.17 * t)
    mono = np.tanh(mono * wobble)
    return np.stack([mono * 0.98, mono], axis=1)


def make_other(n: int) -> np.ndarray:
    t = np.arange(n) / SR
    freqs = (220.0, 277.183, 329.628, 440.0)
    pad = sum(np.sin(2 * np.pi * f * t + i * 0.37) for i, f in enumerate(freqs)) / len(freqs)
    pad *= 0.18 * (0.72 + 0.28 * np.sin(2 * np.pi * 0.095 * t))
    return np.stack([pad, np.roll(pad, 137)], axis=1)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    n = int(SR * DURATION)
    stems = {
        "drums": make_drums(n),
        "bass": make_bass(n),
        "other": make_other(n),
    }
    mixture = sum(stems.values())
    peak = float(np.max(np.abs(mixture)))
    scale = 0.92 / peak
    for name, audio in {**stems, "mixture": mixture}.items():
        sf.write(OUT / f"{name}.wav", audio * scale, SR, subtype="FLOAT")
    print(f"fixture={OUT} duration={DURATION:.1f}s peak_before_scale={peak:.6f} scale={scale:.6f}")


if __name__ == "__main__":
    main()
