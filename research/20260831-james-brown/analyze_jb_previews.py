#!/usr/bin/env python3
"""Mixture-level rhythm descriptors for 30-second Shazam/Apple Music previews.

This does not identify instruments or reconstruct the full recording.  It reports
repeatability, one-bar versus two-bar recurrence, onset density, and broad-band
onset coupling from the exact preview bytes supplied by the catalog.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, stft


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 1e-12 else 0.0


def onset_envelopes(x: np.ndarray, sr: int, hop: int = 256):
    freqs, _, z = stft(
        x,
        fs=sr,
        nperseg=2048,
        noverlap=2048 - hop,
        boundary=None,
        padded=False,
    )
    logmag = np.log1p(20.0 * np.abs(z))
    delta = np.maximum(0.0, np.diff(logmag, axis=1, prepend=logmag[:, :1]))

    masks = {
        "full": np.ones_like(freqs, dtype=bool),
        "low": freqs < 250,
        "mid": (freqs >= 250) & (freqs < 2500),
        "high": freqs >= 2500,
    }
    envs = {}
    for name, mask in masks.items():
        env = delta[mask].mean(axis=0)
        env = gaussian_filter1d(env, sigma=1.0)
        q10, q90 = np.quantile(env, [0.10, 0.90])
        envs[name] = np.clip((env - q10) / max(q90 - q10, 1e-9), 0.0, None)
    return envs, sr / hop


def tempo_candidates(env: np.ndarray, env_rate: float):
    centered = env - np.mean(env)
    corr = np.correlate(centered, centered, mode="full")[len(centered) - 1 :]
    corr /= np.maximum(np.arange(len(corr), 0, -1), 1)
    lo = int(round(env_rate * 60.0 / 160.0))
    hi = int(round(env_rate * 60.0 / 65.0))
    region = corr[lo : hi + 1]
    peaks, _ = find_peaks(region)
    if len(peaks) == 0:
        peaks = np.arange(len(region))
    ranked = peaks[np.argsort(region[peaks])[::-1]]
    out = []
    for p in ranked:
        lag = int(p + lo)
        bpm = 60.0 * env_rate / lag
        if all(abs(np.log2(bpm / old[0])) > 0.035 for old in out):
            out.append((bpm, float(corr[lag])))
        if len(out) == 5:
            break
    return out


def beat_phase(env: np.ndarray, period: float) -> float:
    candidates = np.linspace(0, period, 96, endpoint=False)
    idx = np.arange(len(env))
    scores = []
    for phase in candidates:
        distance = np.abs(((idx - phase + period / 2) % period) - period / 2)
        weights = np.exp(-0.5 * (distance / max(period * 0.08, 1.0)) ** 2)
        scores.append(float(np.dot(env, weights)))
    return float(candidates[int(np.argmax(scores))])


def bar_vectors(env: np.ndarray, period: float, phase: float, subdivisions: int = 16):
    bar = period * 4.0
    step = bar / subdivisions
    vectors = []
    start = phase
    while start + bar <= len(env):
        vec = np.zeros(subdivisions)
        for i in range(subdivisions):
            a = int(round(start + i * step))
            b = int(round(start + (i + 1) * step))
            vec[i] = np.sum(env[max(a, 0) : max(b, a + 1)])
        total = vec.sum()
        if total > 1e-9:
            vectors.append(vec / total)
        start += bar
    return vectors


def lag_similarity(vectors, lag: int):
    if len(vectors) <= lag:
        return None
    return float(np.mean([cosine(vectors[i], vectors[i + lag]) for i in range(len(vectors) - lag)]))


def analyze(path: Path):
    sr, raw = wavfile.read(path)
    x = raw.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x /= max(np.max(np.abs(x)), 1.0)

    envs, env_rate = onset_envelopes(x, sr)
    full = envs["full"]
    candidates = tempo_candidates(full, env_rate)
    evaluated = []
    for candidate_bpm, autocorr in candidates:
        candidate_period = env_rate * 60.0 / candidate_bpm
        candidate_phase = beat_phase(full, candidate_period)
        candidate_vectors = bar_vectors(full, candidate_period, candidate_phase)
        one = lag_similarity(candidate_vectors, 1) or 0.0
        two = lag_similarity(candidate_vectors, 2) or 0.0
        # A funk pulse should reproduce a four-beat bar.  Autocorrelation alone can
        # mistake a dense subdivision or a longer accent cycle for the beat.
        range_penalty = 0.05 if candidate_bpm < 85.0 or candidate_bpm > 140.0 else 0.0
        recurrence_score = one + 0.25 * two + 0.10 * max(autocorr, 0.0) - range_penalty
        evaluated.append(
            (recurrence_score, candidate_bpm, candidate_period, candidate_phase, candidate_vectors)
        )
    _, bpm, period, phase, vectors = max(evaluated, key=lambda item: item[0])

    threshold = np.median(full) + 0.75 * np.std(full)
    peaks, _ = find_peaks(full, height=threshold, distance=max(1, int(env_rate * 0.045)))
    density = len(peaks) / (len(x) / sr)

    one = lag_similarity(vectors, 1)
    two = lag_similarity(vectors, 2)
    template = np.mean(vectors, axis=0) if vectors else np.zeros(16)
    top4 = float(np.sort(template)[-4:].sum() / max(template.sum(), 1e-9))

    band_corr = {}
    for a, b in [("low", "mid"), ("low", "high"), ("mid", "high")]:
        band_corr[f"{a}_{b}"] = float(np.corrcoef(envs[a], envs[b])[0, 1])

    return {
        "file": path.name,
        "duration_seconds": round(len(x) / sr, 3),
        "tempo_estimate_bpm": round(bpm, 2),
        "tempo_candidates_bpm": [round(item[0], 2) for item in candidates],
        "bars_observed": len(vectors),
        "strong_onsets_per_second": round(density, 3),
        "adjacent_bar_similarity": None if one is None else round(one, 4),
        "two_bar_lag_similarity": None if two is None else round(two, 4),
        "two_bar_gain": None if one is None or two is None else round(two - one, 4),
        "top4_subdivision_concentration": round(top4, 4),
        "mean_16th_template": [round(float(v), 4) for v in template],
        "broad_band_onset_correlations": {k: round(v, 4) for k, v in band_corr.items()},
    }


def main(argv):
    results = [analyze(Path(arg)) for arg in argv[1:]]
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv)
