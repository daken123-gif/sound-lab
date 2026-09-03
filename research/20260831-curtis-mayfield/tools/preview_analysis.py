#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import find_peaks, stft

SR = 22050
NFFT = 2048
HOP = 256
BANDS = {"low": (40.0, 250.0), "mid": (250.0, 2000.0), "high": (2000.0, 9000.0)}


def decode(path: Path) -> np.ndarray:
    wav = path.with_suffix(".analysis.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path),
                    "-ac", "1", "-ar", str(SR), str(wav)], check=True)
    sr, data = wavfile.read(wav)
    assert sr == SR
    x = data.astype(np.float64)
    if np.issubdtype(data.dtype, np.integer):
        x /= max(abs(np.iinfo(data.dtype).min), np.iinfo(data.dtype).max)
    return x


def normalize_env(env):
    env = (env - np.median(env)) / (np.std(env) + 1e-12)
    return np.maximum(0.0, env)


def envelopes(x):
    freqs, _, z = stft(x, fs=SR, window="hann", nperseg=NFFT,
                       noverlap=NFFT-HOP, boundary=None, padded=False)
    logmag = np.log1p(10.0 * np.abs(z))
    diff = np.maximum(0.0, np.diff(logmag, axis=1))
    out = {"full": normalize_env(diff.mean(axis=0))}
    for name, (lo, hi) in BANDS.items():
        mask = (freqs >= lo) & (freqs < hi)
        out[name] = normalize_env(diff[mask].mean(axis=0))
    return out


def tempo_candidates(env):
    centered = env - env.mean()
    ac = np.correlate(centered, centered, mode="full")[len(centered)-1:]
    ac /= ac[0] + 1e-12
    min_lag = int(round((60.0 / 200.0) * SR / HOP))
    max_lag = int(round((60.0 / 45.0) * SR / HOP))
    segment = ac[min_lag:max_lag+1]
    peaks, _ = find_peaks(segment, distance=3)
    ranked = sorted(peaks, key=lambda p: segment[p], reverse=True)[:5]
    return [{"bpm": round(60.0*SR/(HOP*(p+min_lag)), 2),
             "strength": round(float(segment[p]), 4)} for p in ranked]


def event_stats(env, duration):
    distance = max(1, int(round(0.09 * SR / HOP)))
    peaks, _ = find_peaks(env, height=1.0, distance=distance, prominence=0.35)
    times = peaks * HOP / SR
    ioi = np.diff(times)
    return {"onset_count": int(len(peaks)),
            "onsets_per_second": round(len(peaks)/duration, 3),
            "median_ioi_s": round(float(np.median(ioi)), 4) if len(ioi) else None,
            "tempo_candidates": tempo_candidates(env)}


def lagged_corr(a, b, max_lag_s=0.24):
    n = min(len(a), len(b))
    a = (a[:n]-a[:n].mean())/(a[:n].std()+1e-12)
    b = (b[:n]-b[:n].mean())/(b[:n].std()+1e-12)
    lim = int(round(max_lag_s*SR/HOP))
    best = (-2.0, 0)
    for lag in range(-lim, lim+1):
        aa, bb = ((a[-lag:], b[:n+lag]) if lag < 0 else
                  (a[:n-lag], b[lag:]) if lag > 0 else (a, b))
        corr = float(np.mean(aa*bb))
        # Prefer the smallest absolute lag when periodic signals yield ties.
        if corr > best[0] + 1e-9 or (abs(corr-best[0]) <= 1e-9 and abs(lag) < abs(best[1])):
            best = (corr, lag)
    return {"correlation": round(best[0], 4),
            "lag_s": round(best[1]*HOP/SR, 4)}


def phase_concentration(env, bpm):
    period_frames = (60.0/bpm)*SR/HOP
    idx = np.arange(len(env))
    weights = np.maximum(env, 0.0)
    phasor = np.sum(weights*np.exp(2j*np.pi*idx/period_frames))
    return round(float(abs(phasor)/(weights.sum()+1e-12)), 4)


def analyze(x, pulse_bpms):
    envs = envelopes(x)
    duration = len(x)/SR
    bands = {}
    for name in ("low", "mid", "high"):
        bands[name] = event_stats(envs[name], duration)
        bands[name]["phase_concentration"] = {
            str(bpm): phase_concentration(envs[name], bpm) for bpm in pulse_bpms
        }
    pairs = {f"{a}_{b}": lagged_corr(envs[a], envs[b])
             for a, b in (("low", "mid"), ("low", "high"), ("mid", "high"))}
    return {"duration_s": round(duration, 4), "pulse_bpms": pulse_bpms,
            "full": event_stats(envs["full"], duration), "bands": bands,
            "cross_band": pairs}


def synthetic_test():
    duration = 12.0
    n = int(duration*SR)
    t = np.arange(n)/SR
    def clicks(freq, delay):
        x = np.zeros(n)
        for when in np.arange(delay, duration, 0.5):
            i = int(when*SR)
            m = min(n-i, int(0.05*SR))
            x[i:i+m] += np.sin(2*np.pi*freq*t[:m])*np.exp(-t[:m]*80)
        return x
    aligned = clicks(100, 0)+clicks(700, 0)+clicks(4000, 0)
    delayed = clicks(100, 0)+clicks(700, 0.08)+clicks(4000, 0.16)
    return {"aligned": analyze(aligned, [120.0])["cross_band"],
            "delayed": analyze(delayed, [120.0])["cross_band"]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("inputs", nargs="*")
    p.add_argument("--pulse", type=float, action="append")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    out = {}
    if args.self_test:
        out["synthetic_test"] = synthetic_test()
    for name in args.inputs:
        out[name] = analyze(decode(Path(name)), args.pulse or [120.0])
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
