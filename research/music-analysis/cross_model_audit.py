#!/usr/bin/env python3
"""Compare MDX A/B weights on a known-stem fixture and two real previews."""

from __future__ import annotations

import json
import struct
from pathlib import Path

import essentia.standard as es
import numpy as np

from essentia_compare import SR
from phase_analysis import phase_features


ROOT = Path(__file__).parent
TRACKS = {
    "Billy Jack": {
        "mixture": ROOT.parent / "quota-probe-5/01-billy-jack.m4a",
        "a_drums": ROOT / "separated/billy-a-drums/01-billy-jack_(Drums)_kuielab_a_drums.wav",
        "b_drums": ROOT / "separated/billy-drums/01-billy-jack_(Drums)_kuielab_b_drums.wav",
        "a_bass": ROOT / "separated/billy-a-bass/01-billy-jack_(Bass)_kuielab_a_bass.wav",
        "b_bass": ROOT / "separated/billy-bass/01-billy-jack_(Bass)_kuielab_b_bass.wav",
    },
    "Sweet Exorcist": {
        "mixture": ROOT.parent / "quota-probe-100-add80/026-43465733.m4a",
        "a_drums": ROOT / "separated/sweet-a-drums/026-43465733_(Drums)_kuielab_a_drums.wav",
        "b_drums": ROOT / "separated/sweet-drums/026-43465733_(Drums)_kuielab_b_drums.wav",
        "a_bass": ROOT / "separated/sweet-a-bass/026-43465733_(Bass)_kuielab_a_bass.wav",
        "b_bass": ROOT / "separated/sweet-bass/026-43465733_(Bass)_kuielab_b_bass.wav",
    },
}


def mono(path: Path) -> np.ndarray:
    return es.MonoLoader(filename=str(path), sampleRate=SR)().astype(np.float64)


def read_float_wav(path: Path) -> np.ndarray:
    """Read the float32 stereo WAVs used by this controlled fixture."""
    raw = path.read_bytes()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError(f"not a RIFF/WAVE file: {path}")
    offset = 12
    fmt = None
    payload = None
    while offset + 8 <= len(raw):
        chunk_id = raw[offset : offset + 4]
        size = struct.unpack_from("<I", raw, offset + 4)[0]
        body = raw[offset + 8 : offset + 8 + size]
        if chunk_id == b"fmt ":
            fmt = struct.unpack_from("<HHIIHH", body)
        elif chunk_id == b"data":
            payload = body
        offset += 8 + size + (size % 2)
    if fmt is None or payload is None:
        raise ValueError(f"missing fmt/data chunk: {path}")
    audio_format, channels, sample_rate, _, _, bits = fmt
    if (audio_format, sample_rate, bits) != (3, SR, 32):
        raise ValueError(f"expected IEEE float32/{SR} Hz, got {fmt}: {path}")
    return np.frombuffer(payload, dtype="<f4").reshape(-1, channels).astype(np.float64)


def align(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = min(len(a), len(b))
    return a[:n].reshape(-1), b[:n].reshape(-1)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    a, b = align(a, b)
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denominator) if denominator else 0.0


def si_sdr(estimate: np.ndarray, target: np.ndarray) -> float:
    estimate, target = align(estimate, target)
    estimate = estimate - estimate.mean()
    target = target - target.mean()
    alpha = np.dot(estimate, target) / (np.dot(target, target) + 1e-18)
    projected = alpha * target
    noise = estimate - projected
    return float(10 * np.log10((np.dot(projected, projected) + 1e-18) / (np.dot(noise, noise) + 1e-18)))


def rms(audio: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(audio))))


def window_features(audio: np.ndarray) -> list[dict[str, object]]:
    rows = []
    for start_s in (0, 10, 20):
        start = start_s * SR
        stop = min(len(audio), (start_s + 10) * SR)
        if stop - start >= 8 * SR:
            rows.append({"seconds": [start_s, round(stop / SR, 3)], **phase_features(audio[start:stop].astype(np.float32))})
    return rows


def fixture_result(stem: str) -> dict[str, object]:
    title = stem.title()
    a_dir = ROOT / f"separated/fixture-a-{stem}"
    b_dir = ROOT / f"separated/fixture-{stem}"
    a_pred = a_dir / f"mixture_({title})_kuielab_a_{stem}.wav"
    a_comp = a_dir / f"mixture_(No {title})_kuielab_a_{stem}.wav"
    b_pred = b_dir / f"mixture_({title})_kuielab_b_{stem}.wav"
    target = read_float_wav(ROOT / f"fixture/{stem}.wav")
    mixture = read_float_wav(ROOT / "fixture/mixture.wav")
    a_audio, complement, b_audio = read_float_wav(a_pred), read_float_wav(a_comp), read_float_wav(b_pred)
    n = min(len(mixture), len(a_audio), len(complement))
    residual = mixture[:n] - a_audio[:n] - complement[:n]
    non_targets = {
        name: read_float_wav(ROOT / f"fixture/{name}.wav")
        for name in ("drums", "bass", "other")
        if name != stem
    }
    result = {
        "target": stem,
        "si_sdr_db": round(si_sdr(a_audio, target), 3),
        "target_cosine": round(cosine(a_audio, target), 4),
        "non_target_cosines": {name: round(cosine(a_audio, audio), 4) for name, audio in non_targets.items()},
        "predicted_rms": round(rms(a_audio), 6),
        "target_rms": round(rms(target), 6),
        "reconstruction_residual_rms": round(rms(residual), 9),
    }
    result["a_vs_b_cosine"] = round(cosine(a_audio, b_audio), 4)
    result["a_vs_b_si_sdr_db"] = round(si_sdr(a_audio, b_audio), 3)
    result["gate"] = {
        "minimum_target_cosine": 0.8,
        "minimum_si_sdr_db": 3.0,
        "passed": result["target_cosine"] >= 0.8 and result["si_sdr_db"] >= 3.0,
    }
    return result


def real_track_result(paths: dict[str, Path], stem: str) -> dict[str, object]:
    a = mono(paths[f"a_{stem}"])
    b = mono(paths[f"b_{stem}"])
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    return {
        "stem": stem,
        "a_vs_b_waveform_cosine": round(cosine(a[:, None], b[:, None]), 4),
        "a_vs_b_waveform_si_sdr_db": round(si_sdr(a[:, None], b[:, None]), 3),
        "model_a": {"full_excerpt": phase_features(a.astype(np.float32)), "windows": window_features(a)},
        "model_b": {"full_excerpt": phase_features(b.astype(np.float32)), "windows": window_features(b)},
    }


def main() -> None:
    fixture = {stem: fixture_result(stem) for stem in ("drums", "bass")}
    if not all(row["gate"]["passed"] for row in fixture.values()):
        raise SystemExit("fixture gate failed; real-track comparison is invalid")
    tracks = {
        title: {stem: real_track_result(paths, stem) for stem in ("drums", "bass")}
        for title, paths in TRACKS.items()
    }
    result = {
        "scope": {
            "comparison": "MDX-Net A weights versus MDX-Net B weights",
            "independence_limit": "same architecture family; this is a weight-sensitivity check, not independent architectural replication",
            "real_track_limit": "estimated stems from 30-second previews, not multitracks",
            "demucs_attempt": "blocked before inference because this sandbox has no readable /proc/cpuinfo and PyTorch state_dict loading fails cpuinfo initialization",
        },
        "fixture": fixture,
        "tracks": tracks,
    }
    output = ROOT / "cross-model-results-20260901.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output.read_text(), end="")


if __name__ == "__main__":
    main()
