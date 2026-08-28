#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import re
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
    else:
        data = samples.astype(np.float64)
    return rate, data


def compare(reference: np.ndarray, candidate: np.ndarray) -> tuple[float, float]:
    common = min(reference.size, candidate.size)
    ref = reference[:common]
    test = candidate[:common]
    error = ref - test
    signal_rms = float(np.sqrt(np.mean(np.square(ref))))
    error_rms = float(np.sqrt(np.mean(np.square(error))))
    snr = float("inf") if error_rms == 0 else 20.0 * math.log10(signal_rms / error_rms)
    return snr, float(np.max(np.abs(error)))


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "aac-bitrate-benchmark")
    generation_rate, generation_reference = read_pcm(root / "generation-source.wav")
    loop_rate, loop_reference = read_pcm(root / "loop-source.wav")
    reference_seam = float(loop_reference[0] - loop_reference[-1])

    generation_rows: list[dict[str, str]] = []
    pattern = re.compile(r"generation-(\d+)-(\d+)-decoded\.wav")
    for path in sorted(root.glob("generation-*-*-decoded.wav")):
        match = pattern.fullmatch(path.name)
        if not match:
            continue
        bitrate, generation = match.groups()
        rate, candidate = read_pcm(path)
        if rate != generation_rate:
            raise ValueError(f"sample rate mismatch: {path}")
        snr, max_error = compare(generation_reference, candidate)
        encoded_path = root / f"generation-{bitrate}-{generation}.m4a"
        generation_rows.append(
            {
                "bitrate_kbps": bitrate,
                "generation": generation,
                "encoded_bytes": str(encoded_path.stat().st_size),
                "frames": str(candidate.size),
                "frame_delta": str(candidate.size - generation_reference.size),
                "snr_db": "inf" if math.isinf(snr) else f"{snr:.3f}",
                "max_abs_error": f"{max_error:.9f}",
            }
        )

    with (root / "generation-results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=generation_rows[0].keys())
        writer.writeheader()
        writer.writerows(generation_rows)

    loop_rows: list[dict[str, str]] = []
    pattern = re.compile(r"loop-(\d+)-decoded\.wav")
    for path in sorted(root.glob("loop-*-decoded.wav")):
        match = pattern.fullmatch(path.name)
        if not match:
            continue
        bitrate = match.group(1)
        rate, candidate = read_pcm(path)
        if rate != loop_rate:
            raise ValueError(f"sample rate mismatch: {path}")
        snr, max_error = compare(loop_reference, candidate)
        intended_last = min(candidate.size, loop_reference.size) - 1
        intended_seam = float(candidate[0] - candidate[intended_last])
        encoded_path = root / f"loop-{bitrate}.m4a"
        loop_rows.append(
            {
                "bitrate_kbps": bitrate,
                "encoded_bytes": str(encoded_path.stat().st_size),
                "frames": str(candidate.size),
                "frame_delta": str(candidate.size - loop_reference.size),
                "snr_db": f"{snr:.3f}",
                "max_abs_error": f"{max_error:.9f}",
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
