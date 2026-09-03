#!/usr/bin/env python3
"""Inspect acquired E-GMD metadata/MIDI and RWC annotation schemas.

The probe deliberately does not claim that audio has been acquired or evaluated.
It records only properties observed in the supplied files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
import wave
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


EGMD_COLUMNS = [
    "drummer",
    "session",
    "id",
    "style",
    "bpm",
    "beat_type",
    "time_signature",
    "duration",
    "split",
    "midi_filename",
    "audio_filename",
    "kit_name",
]
RWC_METADATA_COLUMNS = [
    "RWCID",
    "CollID",
    "PieceNo",
    "CDNo",
    "TrackNo",
    "Title",
    "Artist",
    "SingerInformation",
    "SingingLanguage",
    "Tempo",
    "Variation",
    "LiveInstruments",
    "DrumInformation",
    "Composer",
    "CompositionType",
    "GenreMain",
    "GenreSub",
    "audio_start",
    "audio_end",
    "duration",
]


class ProbeError(ValueError):
    """Raised when acquired public data violates its documented schema."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_dict_rows(path: Path, delimiter: str) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def _midi_header(raw: bytes, context: str) -> tuple[int, int, int]:
    if len(raw) != 14 or raw[:4] != b"MThd":
        raise ProbeError(f"{context}: invalid MIDI header")
    if struct.unpack(">I", raw[4:8])[0] != 6:
        raise ProbeError(f"{context}: unexpected MIDI header length")
    return struct.unpack(">HHH", raw[8:14])


def _missing_cells(rows: Iterable[dict[str, str]], columns: list[str]) -> dict[str, int]:
    row_list = list(rows)
    return {column: sum(not row[column].strip() for row in row_list) for column in columns}


def probe_egmd(metadata_path: Path, midi_zip_path: Path) -> dict[str, Any]:
    columns, rows = _read_dict_rows(metadata_path, ",")
    if columns != EGMD_COLUMNS:
        raise ProbeError(f"E-GMD metadata columns differ: {columns}")
    if not rows:
        raise ProbeError("E-GMD metadata has no rows")

    split_counts = Counter(row["split"] for row in rows)
    if set(split_counts) != {"train", "validation", "test"}:
        raise ProbeError(f"E-GMD split values differ: {sorted(split_counts)}")

    midi_formats: Counter[int] = Counter()
    midi_divisions: Counter[int] = Counter()
    missing_members: list[str] = []
    with zipfile.ZipFile(midi_zip_path) as archive:
        members = set(archive.namelist())
        for row in rows:
            member = f"e-gmd-v1.0.0/{row['midi_filename']}"
            if member not in members:
                missing_members.append(member)
                continue
            with archive.open(member) as handle:
                midi_format, _track_count, division = _midi_header(
                    handle.read(14), member
                )
            midi_formats[midi_format] += 1
            midi_divisions[division] += 1
    if missing_members:
        raise ProbeError(f"E-GMD archive misses {len(missing_members)} MIDI files")

    return {
        "status": "metadata_and_midi_schema_verified",
        "metadata": {
            "sha256": sha256_file(metadata_path),
            "rows": len(rows),
            "columns": columns,
            "missing_cells": _missing_cells(rows, columns),
            "split_counts": dict(sorted(split_counts.items())),
            "unique_sequences": len({row["id"] for row in rows}),
            "unique_kits": len({row["kit_name"] for row in rows}),
        },
        "midi_archive": {
            "sha256": sha256_file(midi_zip_path),
            "midi_files_checked": len(rows),
            "metadata_paths_missing": 0,
            "header_formats": {str(key): value for key, value in sorted(midi_formats.items())},
            "time_divisions": {str(key): value for key, value in sorted(midi_divisions.items())},
        },
        "audio": {"state": "not_acquired", "files_checked": 0},
    }


def _validate_beat_file(path: Path) -> int:
    columns, rows = _read_dict_rows(path, ";")
    if columns != ["t", "beat"] or not rows:
        raise ProbeError(f"{path}: invalid beat schema")
    previous_time: float | None = None
    previous_beat: int | None = None
    for row in rows:
        time = float(row["t"])
        beat_float = float(row["beat"])
        if time < 0 or (previous_time is not None and time <= previous_time):
            raise ProbeError(f"{path}: beat times are not strictly increasing")
        if not beat_float.is_integer() or not 1 <= beat_float <= 16:
            raise ProbeError(f"{path}: invalid beat value {row['beat']}")
        beat = int(beat_float)
        if previous_beat is not None and beat not in (1, previous_beat + 1):
            raise ProbeError(f"{path}: invalid beat transition")
        previous_time, previous_beat = time, beat
    return len(rows)


def _validate_chord_file(path: Path) -> int:
    columns, rows = _read_dict_rows(path, ";")
    if columns != ["t_start", "t_end", "chord"] or not rows:
        raise ProbeError(f"{path}: invalid chord schema")
    for row in rows:
        start, end = float(row["t_start"]), float(row["t_end"])
        if start < 0 or end <= start or not row["chord"].strip():
            raise ProbeError(f"{path}: invalid chord interval")
    return len(rows)


def _validate_melody_file(path: Path) -> int:
    columns, rows = _read_dict_rows(path, ";")
    if columns != ["t", "f0"] or not rows:
        raise ProbeError(f"{path}: invalid melody schema")
    previous_time: float | None = None
    for row in rows:
        time, f0 = float(row["t"]), float(row["f0"])
        if time < 0 or f0 < 0 or (previous_time is not None and time <= previous_time):
            raise ProbeError(f"{path}: invalid melody trajectory")
        previous_time = time
    return len(rows)


def probe_rwc_annotations(root: Path, revision: str) -> dict[str, Any]:
    metadata_path = root / "metadata.csv"
    columns, rows = _read_dict_rows(metadata_path, ";")
    if columns != RWC_METADATA_COLUMNS:
        raise ProbeError(f"RWC metadata columns differ: {columns}")
    if not rows:
        raise ProbeError("RWC metadata has no rows")

    annotations = root / "01_annotations_preprocessed"
    beat_files = sorted((annotations / "beats").glob("RWC-*/*.csv"))
    chord_files = sorted((annotations / "chords").glob("RWC-*/*.csv"))
    melody_files = sorted((annotations / "melody").glob("RWC-*/*.csv"))
    midi_files = sorted((annotations / "MIDI_aligned").glob("RWC-*/*.mid"))
    if not all((beat_files, chord_files, melody_files, midi_files)):
        raise ProbeError("RWC annotation class is empty")

    beat_rows = sum(_validate_beat_file(path) for path in beat_files)
    chord_rows = sum(_validate_chord_file(path) for path in chord_files)
    melody_rows = sum(_validate_melody_file(path) for path in melody_files)

    midi_formats: Counter[int] = Counter()
    midi_divisions: Counter[int] = Counter()
    for path in midi_files:
        with path.open("rb") as handle:
            midi_format, _track_count, division = _midi_header(handle.read(14), str(path))
        midi_formats[midi_format] += 1
        midi_divisions[division] += 1

    return {
        "status": "metadata_and_annotation_schema_verified",
        "source_revision": revision,
        "metadata": {
            "sha256": sha256_file(metadata_path),
            "rows": len(rows),
            "columns": columns,
            "collection_counts": dict(sorted(Counter(row["CollID"] for row in rows).items())),
            "unique_recording_ids": len({row["RWCID"] for row in rows}),
            "missing_cells": _missing_cells(rows, columns),
        },
        "annotations": {
            "beat_files": len(beat_files),
            "beat_rows": beat_rows,
            "chord_files": len(chord_files),
            "chord_rows": chord_rows,
            "melody_files": len(melody_files),
            "melody_rows": melody_rows,
            "aligned_midi_files": len(midi_files),
            "midi_header_formats": {str(key): value for key, value in sorted(midi_formats.items())},
            "midi_time_divisions": {str(key): value for key, value in sorted(midi_divisions.items())},
        },
        "audio": {"state": "not_acquired", "files_checked": 0},
    }


def probe_rwc_audio_zip(
    audio_zip_path: Path,
    annotations_root: Path,
    subset: str,
    expected_md5: str,
) -> dict[str, Any]:
    observed_md5 = md5_file(audio_zip_path)
    if observed_md5 != expected_md5:
        raise ProbeError(
            f"RWC {subset} audio checksum differs: {observed_md5}"
        )

    sample_rates: Counter[int] = Counter()
    channels: Counter[int] = Counter()
    sample_widths: Counter[int] = Counter()
    frame_counts: dict[str, int] = {}
    with zipfile.ZipFile(audio_zip_path) as archive:
        wav_members = sorted(
            name for name in archive.namelist() if name.lower().endswith(".wav")
        )
        if not wav_members:
            raise ProbeError(f"RWC {subset} archive has no WAV files")
        for member in wav_members:
            with archive.open(member) as handle:
                with wave.open(io.BytesIO(handle.read()), "rb") as wav:
                    sample_rates[wav.getframerate()] += 1
                    channels[wav.getnchannels()] += 1
                    sample_widths[wav.getsampwidth()] += 1
                    frame_counts[Path(member).stem] = wav.getnframes()

    audio_ids = set(frame_counts)
    metadata_columns, metadata_rows = _read_dict_rows(
        annotations_root / "metadata.csv", ";"
    )
    if metadata_columns != RWC_METADATA_COLUMNS:
        raise ProbeError("RWC metadata schema differs during audio join")
    metadata_ids = {
        row["RWCID"] for row in metadata_rows if row["CollID"] == subset
    }
    beat_ids = {
        path.stem
        for path in (
            annotations_root
            / "01_annotations_preprocessed"
            / "beats"
            / f"RWC-{subset}"
        ).glob("*.csv")
    }
    midi_ids = {
        path.stem
        for path in (
            annotations_root
            / "01_annotations_preprocessed"
            / "MIDI_aligned"
            / f"RWC-{subset}"
        ).glob("*.mid")
    }
    joins = {
        "metadata_missing_for_audio": sorted(audio_ids - metadata_ids),
        "audio_missing_for_metadata": sorted(metadata_ids - audio_ids),
        "beat_missing_for_audio": sorted(audio_ids - beat_ids),
        "aligned_midi_missing_for_audio": sorted(audio_ids - midi_ids),
    }
    if any(joins.values()):
        raise ProbeError(f"RWC {subset} audio/annotation join differs: {joins}")

    return {
        "state": "checksum_and_schema_verified",
        "subset": subset,
        "md5": observed_md5,
        "wav_files_checked": len(audio_ids),
        "sample_rates": {str(key): value for key, value in sorted(sample_rates.items())},
        "channels": {str(key): value for key, value in sorted(channels.items())},
        "sample_width_bytes": {
            str(key): value for key, value in sorted(sample_widths.items())
        },
        "annotation_join_missing_counts": {
            key: len(value) for key, value in joins.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--egmd-csv", type=Path, required=True)
    parser.add_argument("--egmd-midi-zip", type=Path, required=True)
    parser.add_argument("--rwc-root", type=Path, required=True)
    parser.add_argument("--rwc-revision", required=True)
    parser.add_argument("--rwc-audio-zip", type=Path)
    parser.add_argument("--rwc-audio-subset", default="R")
    parser.add_argument("--rwc-audio-md5")
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "e_gmd": probe_egmd(args.egmd_csv, args.egmd_midi_zip),
        "rwc_annotations": probe_rwc_annotations(args.rwc_root, args.rwc_revision),
    }
    if args.rwc_audio_zip:
        if not args.rwc_audio_md5:
            parser.error("--rwc-audio-md5 is required with --rwc-audio-zip")
        result["rwc_audio_subset"] = probe_rwc_audio_zip(
            args.rwc_audio_zip,
            args.rwc_root,
            args.rwc_audio_subset,
            args.rwc_audio_md5,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
