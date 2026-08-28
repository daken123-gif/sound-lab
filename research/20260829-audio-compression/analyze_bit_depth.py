#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile


def read_normalized(path: Path) -> tuple[int, np.ndarray]:
    rate, samples = wavfile.read(path)
    if samples.dtype == np.float32 or samples.dtype == np.float64:
        normalized = samples.astype(np.float64)
    elif samples.dtype == np.int16:
        normalized = samples.astype(np.float64) / 32768.0
    elif samples.dtype == np.int32:
        # scipy left-justifies 24-bit WAV data in an int32 container.
        normalized = samples.astype(np.float64) / 2147483648.0
    else:
        raise TypeError(f"unsupported sample dtype: {samples.dtype}")
    return rate, normalized


def db(value: float) -> float:
    if value == 0:
        return float("-inf")
    return 20.0 * math.log10(value)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "bit-depth-benchmark")
    rate, reference = read_normalized(root / "source-f32.wav")
    segment_levels = (-6, -60, -90, -110, -130, -150)

    rows: list[dict[str, str]] = []
    for candidate_path in sorted(root.glob("pcm*.wav")):
        candidate_rate, candidate = read_normalized(candidate_path)
        if candidate_rate != rate or candidate.shape != reference.shape:
            raise ValueError(f"shape/rate mismatch: {candidate_path}")

        for index, level in enumerate(segment_levels):
            start = index * 10 * rate
            end = (index + 1) * 10 * rate
            source_segment = reference[start:end]
            candidate_segment = candidate[start:end]
            error = source_segment - candidate_segment
            signal_rms = float(np.sqrt(np.mean(np.square(source_segment))))
            error_rms = float(np.sqrt(np.mean(np.square(error))))
            snr = float("inf") if error_rms == 0 else db(signal_rms / error_rms)
            nonzero_ratio = float(np.count_nonzero(candidate_segment)) / candidate_segment.size

            rows.append(
                {
                    "variant": candidate_path.stem,
                    "segment_dbfs": str(level),
                    "signal_rms_dbfs": f"{db(signal_rms):.3f}",
                    "error_rms_dbfs": f"{db(error_rms):.3f}",
                    "snr_db": "inf" if math.isinf(snr) else f"{snr:.3f}",
                    "nonzero_percent": f"{nonzero_ratio * 100:.3f}",
                }
            )

    with (root / "quality.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
