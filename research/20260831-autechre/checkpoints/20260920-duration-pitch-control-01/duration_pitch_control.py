"""Synthetic analysis control, NOT an Autechre measurement or listening test.

Run: python duration_pitch_control.py > results.json
Requires numpy and scipy. No network, random inputs or audio files.
"""
import hashlib
import json
import sys

import numpy as np
import scipy
from scipy.signal import stft


SR = 24000
ONSET = (0.5 * SR + np.arange(16) * (SR // 4)).astype(int)
N = SR * 5
ROI = slice(ONSET[1], ONSET[-1])  # 14 complete, steady-state intervals


def synth(duration, alternating):
    size = round(duration * SR)
    env = np.ones(size)
    ramp = round(0.005 * SR)
    edge = np.sin(np.linspace(0, np.pi / 2, ramp)) ** 2
    env[:ramp], env[-ramp:] = edge, edge[::-1]
    x, active = np.zeros(N), np.zeros(N, dtype=int)
    frequencies = []
    for i, start in enumerate(ONSET):
        freq = 440 if alternating and i % 2 else 220
        frequencies.append(freq)
        x[start:start + size] += 0.25 * env * np.sin(2 * np.pi * freq * np.arange(size) / SR)
        active[start:start + size] += 1
    return x, active, frequencies


def analyse(x, active):
    f, t, z = stft(x, fs=SR, window="hann", nperseg=1024,
                   noverlap=896, boundary=None, padded=False)
    mag = np.abs(z)
    flux = np.maximum(np.diff(mag, axis=1), 0).sum(axis=0)
    keep = (t[1:] >= ONSET[1] / SR) & (t[1:] < ONSET[-1] / SR)
    flux = flux[keep]
    # Spectral centroid is NOT an estimated musical pitch.
    energy = mag.sum(axis=0)
    sounding = (energy > energy.max() * 0.01) & (t >= ONSET[1] / SR) & (t < ONSET[-1] / SR)
    centroid = (f[:, None] * mag).sum(axis=0) / np.maximum(energy, 1e-15)
    return {
        "scheduled_occupancy_fraction": float(np.mean(active[ROI] > 0)),
        "scheduled_overlap_fraction": float(np.mean(active[ROI] > 1)),
        "waveform_rms": float(np.sqrt(np.mean(x[ROI] ** 2))),
        "spectral_centroid_std_hz": float(np.std(centroid[sounding])),
        "mean_positive_spectral_flux": float(flux.mean()),
        "waveform_sha256_float64le": hashlib.sha256(x.astype("<f8").tobytes()).hexdigest(),
    }, flux


def main():
    cases, fluxes = {}, {}
    for label, duration, alternate in [
        ("short_fixed", 0.05, False), ("short_alternating", 0.05, True),
        ("long_fixed", 0.30, False), ("long_alternating", 0.30, True),
    ]:
        x, active, pitches = synth(duration, alternate)
        metrics, fluxes[label] = analyse(x, active)
        cases[label] = dict(duration_s=duration, frequencies_hz=pitches,
                            onsets_samples=ONSET.tolist(), **metrics)
    comparisons = {}
    for a, b in [("short_fixed", "short_alternating"),
                 ("long_fixed", "long_alternating"),
                 ("short_fixed", "long_fixed"),
                 ("short_alternating", "long_alternating")]:
        comparisons[a + "__" + b] = float(np.corrcoef(fluxes[a], fluxes[b])[0, 1])
    assert all(c["onsets_samples"] == ONSET.tolist() for c in cases.values())
    assert cases["short_fixed"]["scheduled_occupancy_fraction"] == 0.2
    assert cases["long_fixed"]["scheduled_overlap_fraction"] == 0.2
    assert cases["long_fixed"]["scheduled_occupancy_fraction"] == 1.0
    assert np.allclose(fluxes["short_fixed"], analyse(*synth(0.05, False)[:2])[1])
    result = dict(kind="synthetic_control_not_track_analysis", sample_rate=SR,
                  python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__,
                  analysis_interval_s=[ONSET[1] / SR, ONSET[-1] / SR],
                  stft=dict(window="hann", nperseg=1024, hop=128),
                  cases=cases, flux_pearson_comparisons=comparisons,
                  checks="5 assertions passed; scientific generality not tested")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
