#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile


def read_pcm(path: Path) -> tuple[int, np.ndarray]:
    rate, samples = wavfile.read(path)
    if samples.dtype == np.int16:
        data = samples.astype(np.float64) / 32768.0
    elif samples.dtype == np.int32:
        data = samples.astype(np.float64) / 2147483648.0
    elif samples.dtype in (np.float32, np.float64):
        data = samples.astype(np.float64)
    else:
        raise TypeError(f"unsupported dtype {samples.dtype}: {path}")
    return rate, data


def snr_db(reference: np.ndarray, candidate: np.ndarray) -> float:
    signal = float(np.sqrt(np.mean(np.square(reference))))
    error = float(np.sqrt(np.mean(np.square(reference - candidate))))
    if error == 0:
        return float("inf")
    return 20.0 * math.log10(signal / error)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "generation-loop-benchmark")
    reference_rate, reference = read_pcm(root / "generation-source.wav")
    generation_rows: list[dict[str, str]] = []
    for path in sorted(root.glob("generation-*-decoded.wav")):
        rate, candidate = read_pcm(path)
        if rate != reference_rate:
            raise ValueError(f"sample rate mismatch: {path}")
        common = min(reference.size, candidate.size)
        score = snr_db(reference[:common], candidate[:common])
        generation_rows.append(
            {
                "variant": path.stem.removeprefix("generation-").removesuffix("-decoded"),
                "frames": str(candidate.size),
                "frame_delta": str(candidate.size - reference.size),
                "snr_db": "inf" if math.isinf(score) else f"{score:.3f}",
                "max_abs_error": f"{float(np.max(np.abs(reference[:common] - candidate[:common]))):.9f}",
            }
        )

    with (root / "generation-results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=generation_rows[0].keys())
        writer.writeheader()
        writer.writerows(generation_rows)

    loop_rate, loop_reference = read_pcm(root / "loop-source.wav")
    loop_rows: list[dict[str, str]] = []
    reference_seam = float(loop_reference[0] - loop_reference[-1])
    for path in sorted(root.glob("loop-*-decoded.wav")):
        rate, candidate = read_pcm(path)
        if rate != loop_rate:
            raise ValueError(f"sample rate mismatch: {path}")
        common = min(loop_reference.size, candidate.size)
        score = snr_db(loop_reference[:common], candidate[:common])
        raw_seam = float(candidate[0] - candidate[-1])
        intended_last_index = min(loop_reference.size, candidate.size) - 1
        intended_seam = float(candidate[0] - candidate[intended_last_index])
        loop_rows.append(
            {
                "variant": path.stem.removeprefix("loop-").removesuffix("-decoded"),
                "frames": str(candidate.size),
                "frame_delta": str(candidate.size - loop_reference.size),
                "snr_db": "inf" if math.isinf(score) else f"{score:.3f}",
                "raw_seam_step": f"{raw_seam:.9f}",
                "raw_seam_error": f"{abs(raw_seam - reference_seam):.9f}",
                "intended_seam_step": f"{intended_seam:.9f}",
                "intended_seam_error": f"{abs(intended_seam - reference_seam):.9f}",
            }
        )

    with (root / "loop-results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=loop_rows[0].keys())
        writer.writeheader()
        writer.writerows(loop_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
