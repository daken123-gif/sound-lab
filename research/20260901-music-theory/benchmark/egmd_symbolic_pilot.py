#!/usr/bin/env python3
"""E-GMD symbolic pilot for S04, S05, and S10.

Only MIDI note timing, velocity, tempo metadata, and the E-GMD CSV are used.
The script does not inspect audio and does not assign groove quality.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import statistics
import struct
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


class MidiParseError(ValueError):
    """Raised when a MIDI file is outside the supported SMF subset."""


def _read_vlq(data: bytes, position: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if position >= len(data):
            raise MidiParseError("truncated variable-length quantity")
        byte = data[position]
        position += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, position
    raise MidiParseError("variable-length quantity exceeds four bytes")


def parse_midi(data: bytes) -> dict[str, Any]:
    """Parse note-on, tempo, and time-signature events from a Standard MIDI File."""
    if len(data) < 14 or data[:4] != b"MThd":
        raise MidiParseError("missing MThd header")
    header_length = struct.unpack(">I", data[4:8])[0]
    if header_length < 6 or len(data) < 8 + header_length:
        raise MidiParseError("invalid MIDI header length")
    midi_format, track_count, division = struct.unpack(">HHH", data[8:14])
    if division & 0x8000:
        raise MidiParseError("SMPTE time division is unsupported")

    position = 8 + header_length
    notes: list[dict[str, int]] = []
    tempos: list[dict[str, int]] = []
    signatures: list[dict[str, int]] = []
    parsed_tracks = 0
    while parsed_tracks < track_count:
        if position + 8 > len(data) or data[position : position + 4] != b"MTrk":
            raise MidiParseError("missing MTrk chunk")
        length = struct.unpack(">I", data[position + 4 : position + 8])[0]
        track = data[position + 8 : position + 8 + length]
        if len(track) != length:
            raise MidiParseError("truncated MTrk chunk")
        position += 8 + length
        parsed_tracks += 1

        cursor = 0
        tick = 0
        running_status: int | None = None
        while cursor < len(track):
            delta, cursor = _read_vlq(track, cursor)
            tick += delta
            if cursor >= len(track):
                raise MidiParseError("event status is missing")
            first = track[cursor]
            if first & 0x80:
                status = first
                cursor += 1
                first_data: int | None = None
                if status < 0xF0:
                    running_status = status
            else:
                if running_status is None:
                    raise MidiParseError("running status has no channel status")
                status = running_status
                first_data = first
                cursor += 1

            if status == 0xFF:
                if cursor >= len(track):
                    raise MidiParseError("meta event type is missing")
                meta_type = track[cursor]
                cursor += 1
                meta_length, cursor = _read_vlq(track, cursor)
                payload = track[cursor : cursor + meta_length]
                if len(payload) != meta_length:
                    raise MidiParseError("truncated meta event")
                cursor += meta_length
                if meta_type == 0x51 and meta_length == 3:
                    tempos.append({"tick": tick, "microseconds_per_quarter": int.from_bytes(payload, "big")})
                elif meta_type == 0x58 and meta_length >= 2:
                    signatures.append(
                        {"tick": tick, "numerator": payload[0], "denominator": 2 ** payload[1]}
                    )
                continue
            if status in (0xF0, 0xF7):
                sysex_length, cursor = _read_vlq(track, cursor)
                cursor += sysex_length
                if cursor > len(track):
                    raise MidiParseError("truncated system-exclusive event")
                running_status = None
                continue
            if status >= 0xF0:
                raise MidiParseError(f"unsupported system status 0x{status:02x}")

            message_type = status & 0xF0
            data_length = 1 if message_type in (0xC0, 0xD0) else 2
            values = [] if first_data is None else [first_data]
            needed = data_length - len(values)
            if cursor + needed > len(track):
                raise MidiParseError("truncated channel event")
            values.extend(track[cursor : cursor + needed])
            cursor += needed
            if message_type == 0x90 and values[1] > 0:
                notes.append(
                    {
                        "tick": tick,
                        "note": values[0],
                        "velocity": values[1],
                        "channel": status & 0x0F,
                    }
                )

    notes.sort(key=lambda row: (row["tick"], row["note"], row["velocity"]))
    tempos.sort(key=lambda row: row["tick"])
    signatures.sort(key=lambda row: row["tick"])
    return {
        "format": midi_format,
        "division": division,
        "notes": notes,
        "tempos": tempos,
        "time_signatures": signatures,
    }


def signed_grid_residual(tick: int, grid_ticks: float) -> float:
    """Distance to the nearest grid point in [-grid/2, grid/2)."""
    return (tick + grid_ticks / 2.0) % grid_ticks - grid_ticks / 2.0


def _profile_correlation(left: list[float | None], right: list[float | None]) -> tuple[int, float | None]:
    pairs = [(a, b) for a, b in zip(left, right) if a is not None and b is not None]
    if len(pairs) < 4:
        return len(pairs), None
    xs, ys = zip(*pairs)
    x_mean, y_mean = statistics.fmean(xs), statistics.fmean(ys)
    x_var = sum((value - x_mean) ** 2 for value in xs)
    y_var = sum((value - y_mean) ** 2 for value in ys)
    if x_var <= 1e-12 or y_var <= 1e-12:
        return len(pairs), None
    covariance = sum((x - x_mean) * (y - y_mean) for x, y in pairs)
    return len(pairs), covariance / math.sqrt(x_var * y_var)


def _percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def summarize_sequence(row: dict[str, str], midi: dict[str, Any]) -> dict[str, Any]:
    division = midi["division"]
    numerator, denominator = (int(value) for value in row["time_signature"].split("-"))
    grid_ticks = division / 4.0
    bar_ticks = division * 4.0 * numerator / denominator
    slots_per_bar = int(round(bar_ticks / grid_ticks))
    notes = midi["notes"]
    onset_ticks = sorted({event["tick"] for event in notes})
    residuals = [signed_grid_residual(tick, grid_ticks) for tick in onset_ticks]

    slot_residuals: dict[int, list[float]] = defaultdict(list)
    for tick, residual in zip(onset_ticks, residuals):
        slot = int(round((tick % bar_ticks) / grid_ticks)) % slots_per_bar
        slot_residuals[slot].append(residual)
    profile = [
        round(statistics.median(slot_residuals[slot]), 6) if slot in slot_residuals else None
        for slot in range(slots_per_bar)
    ]

    measures: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for event in notes:
        measure = int(event["tick"] // bar_ticks)
        relative_tick = event["tick"] - measure * bar_ticks
        slot = int(round(relative_tick / grid_ticks))
        measures[measure].append((slot, event["note"], event["velocity"]))

    repeated_pairs = 0
    transformed_pairs = 0
    exact_velocity_pairs = 0
    velocity_deltas: list[float] = []
    examples: list[dict[str, Any]] = []
    measure_numbers = sorted(measures)
    for left_measure, right_measure in zip(measure_numbers, measure_numbers[1:]):
        if right_measure != left_measure + 1:
            continue
        left = sorted(measures[left_measure])
        right = sorted(measures[right_measure])
        left_topology = [(slot, note) for slot, note, _ in left]
        right_topology = [(slot, note) for slot, note, _ in right]
        if len(left) < 4 or left_topology != right_topology:
            continue
        repeated_pairs += 1
        deltas = [abs(a[2] - b[2]) for a, b in zip(left, right)]
        mean_delta = statistics.fmean(deltas)
        if mean_delta >= 1.0:
            transformed_pairs += 1
            velocity_deltas.append(mean_delta)
            if len(examples) < 2:
                examples.append(
                    {
                        "measures_zero_based": [left_measure, right_measure],
                        "event_count": len(left),
                        "mean_absolute_velocity_delta": round(mean_delta, 6),
                        "maximum_velocity_delta": max(deltas),
                    }
                )
        else:
            exact_velocity_pairs += 1

    tempo_values = sorted({event["microseconds_per_quarter"] for event in midi["tempos"]})
    tempo_bpms = [60_000_000.0 / value for value in tempo_values]
    return {
        "id": row["id"],
        "style": row["style"],
        "split": row["split"],
        "beat_type": row["beat_type"],
        "time_signature": row["time_signature"],
        "metadata_bpm": float(row["bpm"]),
        "note_on_count": len(notes),
        "unique_onset_count": len(onset_ticks),
        "tempo_event_count": len(midi["tempos"]),
        "distinct_tempo_count": len(tempo_values),
        "tempo_bpms": [round(value, 6) for value in tempo_bpms],
        "tempo_metadata_absolute_bpm_difference": round(
            abs(tempo_bpms[0] - float(row["bpm"])), 9
        ) if len(tempo_bpms) == 1 else None,
        "mean_absolute_sixteenth_residual_ticks": round(
            statistics.fmean(abs(value) for value in residuals), 6
        ) if residuals else None,
        "maximum_absolute_sixteenth_residual_ticks": round(
            max(abs(value) for value in residuals), 6
        ) if residuals else None,
        "signed_residual_profile_ticks": profile,
        "adjacent_quantized_topology_repeat_pairs": repeated_pairs,
        "velocity_transformed_pairs": transformed_pairs,
        "exact_or_subthreshold_velocity_pairs": exact_velocity_pairs,
        "velocity_transformation_mean_deltas": velocity_deltas,
        "velocity_transformation_examples": examples,
    }


def _find_equal_amount_distinct_shape(summaries: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [row for row in summaries if row["mean_absolute_sixteenth_residual_ticks"] is not None]
    candidates.sort(key=lambda row: (row["mean_absolute_sixteenth_residual_ticks"], row["id"]))
    best: tuple[tuple[float, int, float, str, str], dict[str, Any]] | None = None
    for index, left in enumerate(candidates):
        for right in candidates[index + 1 :]:
            amount_gap = abs(
                right["mean_absolute_sixteenth_residual_ticks"]
                - left["mean_absolute_sixteenth_residual_ticks"]
            )
            if amount_gap > 0.25:
                break
            common, correlation = _profile_correlation(
                left["signed_residual_profile_ticks"], right["signed_residual_profile_ticks"]
            )
            if correlation is None or correlation > 0.2:
                continue
            payload = {
                "sequence_ids": [left["id"], right["id"]],
                "mean_absolute_residual_ticks": [
                    left["mean_absolute_sixteenth_residual_ticks"],
                    right["mean_absolute_sixteenth_residual_ticks"],
                ],
                "amount_gap_ticks": round(amount_gap, 6),
                "common_profile_slots": common,
                "signed_profile_correlation": round(correlation, 6),
            }
            key = (amount_gap, -common, correlation, left["id"], right["id"])
            if best is None or key < best[0]:
                best = (key, payload)
    return best[1] if best else None


def run_pilot(metadata_path: Path, midi_zip_path: Path) -> dict[str, Any]:
    with metadata_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    canonical = [row for row in rows if row["kit_name"] == "Acoustic Kit"]
    if len(canonical) != len({row["id"] for row in rows}):
        raise ValueError("Acoustic Kit does not provide exactly one canonical row per sequence id")
    canonical.sort(key=lambda row: row["id"])

    summaries = []
    with zipfile.ZipFile(midi_zip_path) as archive:
        for row in canonical:
            member = f"e-gmd-v1.0.0/{row['midi_filename']}"
            summaries.append(summarize_sequence(row, parse_midi(archive.read(member))))

    fixed_tempo = [row for row in summaries if row["distinct_tempo_count"] == 1]
    fixed_with_microtiming = [
        row for row in fixed_tempo
        if (row["mean_absolute_sixteenth_residual_ticks"] or 0) >= 2.0
    ]
    residual_amounts = [
        row["mean_absolute_sixteenth_residual_ticks"]
        for row in summaries
        if row["mean_absolute_sixteenth_residual_ticks"] is not None
    ]
    topology_repeat_sequences = [
        row for row in summaries if row["adjacent_quantized_topology_repeat_pairs"] > 0
    ]
    transformed_sequences = [row for row in summaries if row["velocity_transformed_pairs"] > 0]
    all_velocity_deltas = [
        value for row in summaries for value in row["velocity_transformation_mean_deltas"]
    ]
    beat_type_breakdown = {}
    for beat_type in sorted({row["beat_type"] for row in summaries}):
        group = [row for row in summaries if row["beat_type"] == beat_type]
        beat_type_breakdown[beat_type] = {
            "sequences": len(group),
            "with_adjacent_quantized_topology_repeat": sum(
                row["adjacent_quantized_topology_repeat_pairs"] > 0 for row in group
            ),
            "with_velocity_transformation": sum(
                row["velocity_transformed_pairs"] > 0 for row in group
            ),
        }
    exemplar = max(
        transformed_sequences,
        key=lambda row: max(row["velocity_transformation_mean_deltas"]),
        default=None,
    )

    return {
        "schema_version": 1,
        "dataset": "E-GMD v1.0.0 MIDI-only archive",
        "selection": {
            "unit": "unique performance sequence id",
            "canonical_kit": "Acoustic Kit",
            "sequences_analyzed": len(summaries),
            "excluded_rerecording_rows": len(rows) - len(summaries),
            "split_counts": dict(sorted(Counter(row["split"] for row in summaries).items())),
            "beat_type_counts": dict(
                sorted(Counter(row["beat_type"] for row in summaries).items())
            ),
            "reason": "avoid treating kit rerecordings of one performance as independent symbolic observations",
        },
        "s04_tempo_vs_microtiming": {
            "fixed_tempo_map_sequences": len(fixed_tempo),
            "fixed_tempo_with_mean_absolute_sixteenth_residual_at_least_2_ticks": len(fixed_with_microtiming),
            "maximum_tempo_metadata_absolute_bpm_difference": round(
                max(row["tempo_metadata_absolute_bpm_difference"] for row in fixed_tempo), 9
            ) if fixed_tempo else None,
            "mean_absolute_sixteenth_residual_ticks": {
                "minimum": round(_percentile(residual_amounts, 0.0), 6),
                "p25": round(_percentile(residual_amounts, 0.25), 6),
                "median": round(_percentile(residual_amounts, 0.5), 6),
                "p75": round(_percentile(residual_amounts, 0.75), 6),
                "maximum": round(_percentile(residual_amounts, 1.0), 6),
            },
            "criterion": "one distinct MIDI tempo value plus mean absolute distance from nearest sixteenth >= 2 ticks",
            "interpretation": "a fixed tempo map can coexist with local onset displacement",
        },
        "s05_deviation_amount_vs_shape": {
            "equal_amount_distinct_shape_example": _find_equal_amount_distinct_shape(summaries),
            "groove_quality_ground_truth": None,
            "interpretation": "scalar deviation amount does not preserve signed timing shape; groove quality is not evaluated",
        },
        "s10_velocity_transformation": {
            "sequences_with_adjacent_quantized_topology_repeat": len(topology_repeat_sequences),
            "sequences_with_velocity_transformation": len(transformed_sequences),
            "transformed_adjacent_measure_pairs": sum(row["velocity_transformed_pairs"] for row in summaries),
            "beat_type_breakdown": beat_type_breakdown,
            "minimum_mean_absolute_velocity_delta": 1.0,
            "median_pair_mean_absolute_velocity_delta": round(statistics.median(all_velocity_deltas), 6)
            if all_velocity_deltas else None,
            "maximum_pair_mean_absolute_velocity_delta": round(max(all_velocity_deltas), 6)
            if all_velocity_deltas else None,
            "exemplar": {
                "sequence_id": exemplar["id"],
                "style": exemplar["style"],
                "examples": exemplar["velocity_transformation_examples"],
            } if exemplar else None,
            "interpretation": "equal quantized note/onset topology is not an exact event repeat when velocity changes",
        },
        "non_inferences": [
            "no audio was acquired or analyzed",
            "MIDI velocity is not calibrated acoustic loudness",
            "nearest-sixteenth residual is an operational grid, not a universal groove model",
            "style and beat_type labels are not groove-quality judgments",
            "quantized topology equality does not imply identical raw timing or sound",
        ],
    }


def verify_parser_against_mido(
    metadata_path: Path, midi_zip_path: Path, sample_count: int
) -> dict[str, Any]:
    """Cross-check a deterministic sample against the independent mido parser."""
    try:
        import mido
        from importlib.metadata import version
    except ImportError as exc:
        raise RuntimeError("--verify-with-mido requires mido") from exc
    with metadata_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = sorted(
            (row for row in csv.DictReader(handle) if row["kit_name"] == "Acoustic Kit"),
            key=lambda row: row["id"],
        )
    if not 1 <= sample_count <= len(rows):
        raise ValueError("mido verification sample count is outside the available sequences")
    indices = sorted({round(index * (len(rows) - 1) / max(1, sample_count - 1)) for index in range(sample_count)})
    checked = []
    with zipfile.ZipFile(midi_zip_path) as archive:
        for index in indices:
            row = rows[index]
            raw = archive.read(f"e-gmd-v1.0.0/{row['midi_filename']}")
            observed = parse_midi(raw)
            reference = mido.MidiFile(file=io.BytesIO(raw))
            notes = []
            tempos = []
            signatures = []
            for track in reference.tracks:
                tick = 0
                for message in track:
                    tick += message.time
                    if message.type == "note_on" and message.velocity > 0:
                        notes.append(
                            {"tick": tick, "note": message.note, "velocity": message.velocity,
                             "channel": message.channel}
                        )
                    elif message.type == "set_tempo":
                        tempos.append({"tick": tick, "microseconds_per_quarter": message.tempo})
                    elif message.type == "time_signature":
                        signatures.append(
                            {"tick": tick, "numerator": message.numerator,
                             "denominator": message.denominator}
                        )
            notes.sort(key=lambda item: (item["tick"], item["note"], item["velocity"]))
            tempos.sort(key=lambda item: item["tick"])
            signatures.sort(key=lambda item: item["tick"])
            if (
                observed["division"] != reference.ticks_per_beat
                or observed["notes"] != notes
                or observed["tempos"] != tempos
                or observed["time_signatures"] != signatures
            ):
                raise MidiParseError(f"mido cross-check differs for {row['id']}")
            checked.append({"id": row["id"], "note_on_count": len(notes)})
    return {
        "reference_parser": f"mido {version('mido')}",
        "selection": "evenly spaced after sorting canonical sequence ids",
        "samples_checked": len(checked),
        "all_event_streams_equal": True,
        "samples": checked,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--midi-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-with-mido", type=int, default=0, metavar="N")
    args = parser.parse_args()
    payload = run_pilot(args.metadata, args.midi_zip)
    if args.verify_with_mido:
        payload["parser_cross_check"] = verify_parser_against_mido(
            args.metadata, args.midi_zip, args.verify_with_mido
        )
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
