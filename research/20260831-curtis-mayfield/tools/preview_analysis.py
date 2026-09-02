#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks, stft


FILES = [
    "billy-jack-preview.m4a",
    "billy-jack-berlin-live-preview.m4a",
    "sweet-exorcist-original-preview.m4a",
    "sweet-exorcist-remaster-preview.m4a",
]
SR = 22050
HOP = 256


def decode(path: Path) -> np.ndarray:
    wav = path.with_suffix(".analysis.wav")
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-y", "-i", str(path),
            "-ac", "1", "-ar", str(SR), str(wav),
        ],
        check=True,
    )
    sr, data = wavfile.read(wav)
    assert sr == SR
    x = data.astype(np.float64)
    if np.issubdtype(data.dtype, np.integer):
        x /= max(abs(np.iinfo(data.dtype).min), np.iinfo(data.dtype).max)
    return x


def onset_envelope(x: np.ndarray):
    _, _, z = stft(
        x,
        fs=SR,
        window="hann",
        nperseg=2048,
        noverlap=2048 - HOP,
        boundary=None,
        padded=False,
    )
    mag = np.abs(z)
    logmag = np.log1p(10.0 * mag)
    flux = np.maximum(0.0, np.diff(logmag, axis=1)).mean(axis=0)
    flux = (flux - np.median(flux)) / (np.std(flux) + 1e-12)
    flux = np.maximum(0.0, flux)
    return flux, mag[:, 1:]


def tempo_candidates(env: np.ndarray):
    centered = env - env.mean()
    ac = np.correlate(centered, centered, mode="full")[len(centered) - 1:]
    ac /= ac[0] + 1e-12
    min_bpm, max_bpm = 45.0, 200.0
    min_lag = int(round((60.0 / max_bpm) * SR / HOP))
    max_lag = int(round((60.0 / min_bpm) * SR / HOP))
    segment = ac[min_lag:max_lag + 1]
    peaks, _ = find_peaks(segment, distance=3)
    ranked = sorted(peaks, key=lambda p: segment[p], reverse=True)[:8]
    out = []
    for p in ranked:
        lag = p + min_lag
        out.append({
            "bpm": round(60.0 * SR / (HOP * lag), 2),
            "strength": round(float(ac[lag]), 4),
        })
    return out


def analyze(x: np.ndarray):
    env, mag = onset_envelope(x)
    distance = max(1, int(round(0.09 * SR / HOP)))
    peaks, props = find_peaks(env, height=1.0, distance=distance, prominence=0.35)
    times = peaks * HOP / SR
    ioi = np.diff(times)

    freqs = np.fft.rfftfreq(2048, 1.0 / SR)
    centroid = (freqs[:, None] * mag).sum(axis=0) / (mag.sum(axis=0) + 1e-12)
    frame_rms = np.sqrt(
        np.convolve(x * x, np.ones(2048) / 2048.0, mode="valid")[::HOP]
    )
    return {
        "duration_s": round(len(x) / SR, 4),
        "onset_count": int(len(peaks)),
        "onsets_per_second": round(len(peaks) / (len(x) / SR), 3),
        "median_ioi_s": round(float(np.median(ioi)), 4) if len(ioi) else None,
        "rms_dbfs": round(20.0 * np.log10(np.sqrt(np.mean(x * x)) + 1e-12), 2),
        "peak_dbfs": round(20.0 * np.log10(np.max(np.abs(x)) + 1e-12), 2),
        "spectral_centroid_hz_median": round(float(np.median(centroid)), 1),
        "tempo_candidates": tempo_candidates(env),
        "onset_envelope": env,
        "rms_envelope": frame_rms,
    }


def aligned_envelope_correlation(a: np.ndarray, b: np.ndarray):
    n = min(len(a), len(b))
    a = (a[:n] - np.mean(a[:n])) / (np.std(a[:n]) + 1e-12)
    b = (b[:n] - np.mean(b[:n])) / (np.std(b[:n]) + 1e-12)
    max_lag = int(round(2.0 * SR / HOP))
    best = (-2.0, 0)
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            aa, bb = a[-lag:], b[:n + lag]
        elif lag > 0:
            aa, bb = a[:n - lag], b[lag:]
        else:
            aa, bb = a, b
        if len(aa) < 50:
            continue
        corr = float(np.mean(aa * bb))
        if corr > best[0]:
            best = (corr, lag)
    return {
        "correlation": round(best[0], 4),
        "lag_s": round(best[1] * HOP / SR, 4),
    }


def main():
    full = {}
    public = {}
    for name in FILES:
        x = decode(Path(name))
        result = analyze(x)
        full[name] = result
        public[name] = {k: v for k, v in result.items() if not k.endswith("envelope")}

    comparisons = {
        "sweet_original_vs_remaster_onset": aligned_envelope_correlation(
            full["sweet-exorcist-original-preview.m4a"]["onset_envelope"],
            full["sweet-exorcist-remaster-preview.m4a"]["onset_envelope"],
        ),
        "sweet_original_vs_remaster_rms": aligned_envelope_correlation(
            full["sweet-exorcist-original-preview.m4a"]["rms_envelope"],
            full["sweet-exorcist-remaster-preview.m4a"]["rms_envelope"],
        ),
    }
    print(json.dumps({"files": public, "comparisons": comparisons}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
