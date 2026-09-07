#!/usr/bin/env python3
"""Apply the existing calibrated features to explicitly located windows of an asset."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import scipy
from analyze_previews import finite
from calibrate_analyzer import (
    SR, frame_rms, onset_times, periodicity_candidates, rms_dbfs,
    spectral_centroid, stereo_balance,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--window-seconds", type=float, default=30)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not 1 <= args.window_seconds <= 60:
        raise ValueError("Use windows between 1 and 60 seconds")
    manifest = json.loads(args.manifest.read_text())
    digest = hashlib.sha256(args.audio.read_bytes()).hexdigest()
    if digest != manifest["sha256"]:
        raise ValueError("Audio does not match the source manifest")
    with tempfile.TemporaryDirectory(dir=args.audio.parent) as temporary:
        pcm = Path(temporary) / "analysis.pcm"
        subprocess.run([
            "ffmpeg", "-v", "error", "-xerror", "-i", str(args.audio),
            "-map", "0:a:0", "-ar", str(SR), "-ac", "2", "-f", "f32le", str(pcm)
        ], check=True, timeout=180)
        if pcm.stat().st_size == 0 or pcm.stat().st_size % 8:
            raise ValueError("Invalid stereo float32 PCM")
        decoded = np.memmap(pcm, dtype="<f4", mode="r").reshape(-1, 2)
        duration = len(decoded) / SR
        if abs(duration - manifest["decoded_duration_s"]) > 0.1:
            raise ValueError("Decoded duration disagrees with acquisition manifest")
        width = round(args.window_seconds * SR)
        windows = []
        for start in range(0, len(decoded), width):
            stop = min(start + width, len(decoded))
            audio = decoded[start:stop].astype(np.float64)
            onsets = onset_times(audio, SR)
            intervals = np.diff(onsets)
            frame_db = 20 * np.log10(np.maximum(frame_rms(audio), 1e-15))
            windows.append({
                "start_s": start / SR, "end_s": stop / SR,
                "duration_s": (stop - start) / SR,
                "rms_dbfs": finite(rms_dbfs(audio), 2),
                "frame_rms_dbfs_p10_p50_p90": [finite(np.percentile(frame_db, p), 2) for p in (10, 50, 90)],
                "spectral_centroid_hz": finite(spectral_centroid(audio, SR), 1),
                "stereo_balance_minus_left_plus_right": finite(stereo_balance(audio), 4),
                "onset_count": int(len(onsets)),
                "onsets_per_second": finite(len(onsets) * SR / len(audio), 3),
                "onset_interval_median_s": finite(np.median(intervals), 4) if len(intervals) else None,
                "onset_interval_cv": finite(np.std(intervals) / np.mean(intervals), 3) if len(intervals) else None,
                "periodicity_candidates_bpm": [finite(v, 2) for v in periodicity_candidates(audio, SR)[:8]],
            })
        del decoded
    root = Path(__file__).parent
    report = {
        "source_sha256": digest,
        "source_page": manifest["source_page"],
        "sample_rate": SR,
        "duration_s": duration,
        "window_seconds": args.window_seconds,
        "scope": "complete decoded asset; absolute offsets within this asset, not asserted as another master",
        "limitations": "Onsets are threshold-dependent event candidates; periodicity candidates are not verified beats. Encoding and window boundaries affect features. No preview alignment or performer/intent inference.",
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "code_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in [
            "analyze_source_windows.py", "analyze_previews.py", "calibrate_analyzer.py"]},
        "windows": windows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"duration_s": duration, "windows": len(windows), "source_sha256": digest}))


if __name__ == "__main__":
    main()
