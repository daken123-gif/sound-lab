#!/usr/bin/env python3
"""R02: compare three decoded Bandcamp previews with identical signal metrics."""

import hashlib
import json
import pathlib
import wave

import numpy as np


ROOT = pathlib.Path("/tmp/aphex-r02")
BAND_EDGES = [20, 150, 500, 2_000, 6_000, 16_000]


def percentile_dict(values, points):
    return {f"p{point}": float(value) for point, value in zip(points, np.percentile(values, points))}


def analyse(path):
    with wave.open(str(path), "rb") as audio:
        rate = audio.getframerate()
        channels = audio.getnchannels()
        width = audio.getsampwidth()
        frames = audio.getnframes()
        assert width == 2
        samples = np.frombuffer(audio.readframes(frames), dtype="<i2").astype(np.float64)
    samples = samples.reshape(-1, channels) / 32768.0

    rms_step = round(rate * 0.1)
    trimmed = samples[: len(samples) // rms_step * rms_step]
    rms = np.sqrt(np.mean(trimmed.reshape(-1, rms_step, channels) ** 2, axis=(1, 2)))
    rms_db = 20 * np.log10(np.maximum(rms, 1e-12))

    size, hop = 2048, 512
    window = np.hanning(size)
    frequencies = np.fft.rfftfreq(size, 1 / rate)
    band_rows, flux = [], []
    previous = None
    for start in range(0, len(samples) - size + 1, hop):
        power = np.mean(
            np.abs(np.fft.rfft(samples[start : start + size] * window[:, None], axis=0)) ** 2,
            axis=1,
        )
        band_rows.append(
            [float(power[(frequencies >= low) & (frequencies < high)].sum()) for low, high in zip(BAND_EDGES[:-1], BAND_EDGES[1:])]
        )
        magnitude = np.sqrt(power)
        normalised = magnitude / (magnitude.sum() + 1e-20)
        if previous is not None:
            flux.append(float(np.maximum(normalised - previous, 0).sum()))
        previous = normalised

    band_rows = np.asarray(band_rows)
    centres = np.arange(len(band_rows)) * hop / rate + size / (2 * rate)
    seconds = []
    for second in range(int(len(samples) / rate)):
        vector = band_rows[(centres >= second) & (centres < second + 1)].sum(axis=0)
        seconds.append(vector / (vector.sum() + 1e-20))
    seconds = np.asarray(seconds)

    candidates = []
    # Exclude intros/outros so that silence and fades do not dominate the candidates.
    for second in range(10, len(seconds) - 15):
        before, after = seconds[second - 2 : second].mean(axis=0), seconds[second : second + 2].mean(axis=0)
        distance = float(np.sqrt(np.sum((np.sqrt(before) - np.sqrt(after)) ** 2) / 2))
        candidates.append((distance, second))
    selected = []
    for distance, second in sorted(candidates, reverse=True):
        if all(abs(second - old_second) >= 10 for _, old_second in selected):
            selected.append((distance, second))
        if len(selected) == 3:
            break

    return {
        "id": path.stem,
        "sample_rate": rate,
        "channels": channels,
        "decoded_seconds": frames / rate,
        "pcm_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rms_100ms_dbfs": percentile_dict(rms_db, [10, 50, 90]),
        "rms_p90_minus_p10_db": float(np.percentile(rms_db, 90) - np.percentile(rms_db, 10)),
        "normalised_positive_spectral_flux": percentile_dict(flux, [50, 90]),
        "spectral_change_candidates": [
            {"time_s": second, "hellinger_distance": distance}
            for distance, second in sorted(selected, key=lambda item: item[1])
        ],
    }


results = [analyse(path) for path in sorted(ROOT.glob("A*.wav"))]
print(json.dumps(results, ensure_ascii=False, indent=2))
