"""Bandwise audit of Flutter preview around 25–30 s.

Usage: python analyze_bands.py INPUT.m4a > results.json
The source hash is fixed. This is signal description, not voice or cause identification.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


EXPECTED = "ab5d3f767f96e3d62e4abd494654e75974f2579542e113ae8fc0a20d59ebc751"
SR, N, HOP = 22050, 2048, 256
BANDS = {"low_40_200": (40, 200), "mid_200_2000": (200, 2000), "high_2000_10000": (2000, 10000)}


def median_rows(t, values, spans):
    return [float(np.median(values[(t >= a) & (t < b)])) for a, b in spans]


src = Path(sys.argv[1])
assert hashlib.sha256(src.read_bytes()).hexdigest() == EXPECTED, "Different source asset"
p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-ac", "1", "-ar", str(SR),
                    "-f", "f32le", "pipe:1"], capture_output=True, check=True)
x = np.frombuffer(p.stdout, dtype="<f4").astype(float)
frames = np.lib.stride_tricks.sliding_window_view(x, N)[::HOP]
t = (np.arange(len(frames)) * HOP + N / 2) / SR
mag = np.abs(np.fft.rfft(frames * np.hanning(N), axis=1))
power = mag ** 2
freq = np.fft.rfftfreq(N, 1 / SR)
norm = mag / np.maximum(mag.sum(axis=1, keepdims=True), 1e-20)
positive_change = np.vstack([np.zeros(norm.shape[1]), np.maximum(np.diff(norm, axis=0), 0)])
total_power = np.maximum(power.sum(axis=1), 1e-20)

spans = [(20, 25), (25, 30), (30, 35)]
seconds = [(a, a + 1) for a in range(20, 35)]
bands = {}
for name, (lo, hi) in BANDS.items():
    mask = (freq >= lo) & (freq < hi)
    band_power = power[:, mask].sum(axis=1)
    band_flux = positive_change[:, mask].sum(axis=1)
    peak = max(float(band_power.max()), 1e-20)
    power_db_rel_peak = 10 * np.log10(np.maximum(band_power, 1e-20) / peak)
    power_share = band_power / total_power
    bands[name] = {
        "aggregate_5s": [
            {"start_s": a, "end_s": b,
             "power_db_rel_band_peak_median": v1,
             "power_share_median": v2,
             "positive_global_normalized_flux_median": v3,
             "positive_global_normalized_flux_p90": v4}
            for (a, b), v1, v2, v3, v4 in zip(
                spans,
                median_rows(t, power_db_rel_peak, spans),
                median_rows(t, power_share, spans),
                median_rows(t, band_flux, spans),
                [float(np.quantile(band_flux[(t >= a) & (t < b)], .9)) for a, b in spans])
        ],
        "one_second_medians": [
            {"start_s": a,
             "power_db_rel_band_peak": v1,
             "power_share": v2,
             "positive_global_normalized_flux": v3}
            for (a, _), v1, v2, v3 in zip(
                seconds,
                median_rows(t, power_db_rel_peak, seconds),
                median_rows(t, power_share, seconds),
                median_rows(t, band_flux, seconds))
        ]
    }

result = {
    "kind": "fixed_flutter_preview_bandwise_transition_audit",
    "source_sha256": EXPECTED,
    "decoded_seconds": len(x) / SR,
    "method": {
        "sample_rate": SR, "frame": N, "hop": HOP,
        "bands_hz_half_open": BANDS,
        "power": "Hann-windowed STFT band power; dB relative to each band's preview-wide maximum",
        "power_share": "band power / total 0..Nyquist power per frame",
        "flux": "positive change of globally L1-normalized magnitude, summed inside band; band contributions are additive"
    },
    "bands": bands,
    "limits": [
        "Preview time is not full-track time.",
        "Band activity does not identify an instrument or compositional cause.",
        "Medians can hide short events; p90 is included for 5-second spans.",
        "Bins above 10 kHz are excluded from named bands."
    ]
}
if len(sys.argv) > 2:
    out = Path(sys.argv[2])
    colors = {"low_40_200": "#276749", "mid_200_2000": "#b7791f", "high_2000_10000": "#6b46c1"}
    labels = {"low_40_200": "40–200 Hz", "mid_200_2000": "200–2000 Hz", "high_2000_10000": "2–10 kHz"}
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True, layout="constrained")
    for name in BANDS:
        rows = bands[name]["one_second_medians"]
        xs = np.array([r["start_s"] + .5 for r in rows])
        axes[0].plot(xs, [r["power_db_rel_band_peak"] for r in rows], marker="o", color=colors[name], label=labels[name])
        axes[1].plot(xs, [100 * r["power_share"] for r in rows], marker="o", color=colors[name])
        axes[2].plot(xs, [r["positive_global_normalized_flux"] for r in rows], marker="o", color=colors[name])
    axes[0].set_ylabel("Power (dB rel. band peak)")
    axes[1].set_ylabel("Power share (%)")
    axes[2].set_ylabel("Positive spectral change")
    axes[2].set_xlabel("Seconds within preview")
    axes[0].legend(ncol=3, frameon=False)
    for ax in axes:
        ax.axvspan(25, 30, color="#cbd5e0", alpha=.25)
        ax.grid(alpha=.2)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Flutter preview: bandwise change around 25–30 s")
    fig.savefig(out, dpi=140)
    plt.close(fig)
print(json.dumps(result, indent=2))
