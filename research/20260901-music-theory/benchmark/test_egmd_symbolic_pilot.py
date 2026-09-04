import csv
import io
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from egmd_symbolic_pilot import (
    MidiParseError,
    _find_equal_amount_distinct_shape,
    parse_midi,
    run_pilot,
    signed_grid_residual,
    summarize_sequence,
)


def vlq(value: int) -> bytes:
    parts = [value & 0x7F]
    value >>= 7
    while value:
        parts.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(parts))


def midi_file(note_events, tempo=500_000) -> bytes:
    conductor = b"".join(
        [
            vlq(0) + b"\xff\x51\x03" + tempo.to_bytes(3, "big"),
            vlq(0) + b"\xff\x58\x04\x04\x02\x18\x08",
            vlq(0) + b"\xff\x2f\x00",
        ]
    )
    track = bytearray()
    previous = 0
    for tick, note, velocity in sorted(note_events):
        track.extend(vlq(tick - previous))
        track.extend(bytes([0x99, note, velocity]))
        previous = tick
    track.extend(vlq(0) + b"\xff\x2f\x00")
    header = b"MThd" + struct.pack(">IHHH", 6, 1, 2, 480)
    return (
        header
        + b"MTrk" + struct.pack(">I", len(conductor)) + conductor
        + b"MTrk" + struct.pack(">I", len(track)) + bytes(track)
    )


class MidiParserTests(unittest.TestCase):
    def test_parses_tempo_signature_and_note_ons(self):
        parsed = parse_midi(midi_file([(0, 36, 90), (125, 42, 70)]))
        self.assertEqual(parsed["division"], 480)
        self.assertEqual(parsed["tempos"], [{"tick": 0, "microseconds_per_quarter": 500000}])
        self.assertEqual(parsed["time_signatures"][0]["denominator"], 4)
        self.assertEqual([row["tick"] for row in parsed["notes"]], [0, 125])

    def test_rejects_smpte_division(self):
        data = b"MThd" + struct.pack(">IHHH", 6, 0, 0, 0xE728)
        with self.assertRaises(MidiParseError):
            parse_midi(data)

    def test_signed_grid_residual_wraps_to_nearest_point(self):
        self.assertEqual(signed_grid_residual(125, 120), 5)
        self.assertEqual(signed_grid_residual(235, 120), -5)


class SequenceEvidenceTests(unittest.TestCase):
    def test_same_quantized_topology_with_velocity_change(self):
        first = [(tick, 36 + index, 60 + index) for index, tick in enumerate((0, 120, 240, 360))]
        second = [(tick + 1920, note, velocity + 12) for tick, note, velocity in first]
        row = {
            "id": "example/1",
            "style": "test",
            "split": "train",
            "beat_type": "beat",
            "time_signature": "4-4",
            "bpm": "120",
        }
        summary = summarize_sequence(row, parse_midi(midi_file(first + second)))
        self.assertEqual(summary["adjacent_quantized_topology_repeat_pairs"], 1)
        self.assertEqual(summary["velocity_transformed_pairs"], 1)
        self.assertEqual(summary["velocity_transformation_mean_deltas"], [12.0])

    def test_equal_amount_can_have_different_signed_shape(self):
        rows = [
            {"id": "a", "mean_absolute_sixteenth_residual_ticks": 5.0,
             "signed_residual_profile_ticks": [5.0, -5.0, 5.0, -5.0]},
            {"id": "b", "mean_absolute_sixteenth_residual_ticks": 5.1,
             "signed_residual_profile_ticks": [-5.0, 5.0, -5.0, 5.0]},
        ]
        result = _find_equal_amount_distinct_shape(rows)
        self.assertEqual(result["sequence_ids"], ["a", "b"])
        self.assertEqual(result["signed_profile_correlation"], -1.0)

    def test_run_pilot_uses_one_acoustic_kit_row_per_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = root / "metadata.csv"
            archive = root / "midi.zip"
            fieldnames = [
                "drummer", "session", "id", "style", "bpm", "beat_type",
                "time_signature", "duration", "split", "midi_filename",
                "audio_filename", "kit_name",
            ]
            rows = []
            for identifier in ("seq/a", "seq/b"):
                rows.append({
                    "drummer": "d", "session": "s", "id": identifier,
                    "style": "test", "bpm": "120", "beat_type": "beat",
                    "time_signature": "4-4", "duration": "4", "split": "train",
                    "midi_filename": identifier.replace("/", "_") + ".midi",
                    "audio_filename": identifier.replace("/", "_") + ".wav",
                    "kit_name": "Acoustic Kit",
                })
            with metadata.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            events = [(10, 36, 70), (130, 38, 72), (250, 42, 74), (370, 46, 76)]
            with zipfile.ZipFile(archive, "w") as handle:
                for row in rows:
                    handle.writestr("e-gmd-v1.0.0/" + row["midi_filename"], midi_file(events))
            result = run_pilot(metadata, archive)
            self.assertEqual(result["selection"]["sequences_analyzed"], 2)
            self.assertEqual(result["selection"]["excluded_rerecording_rows"], 0)
            self.assertEqual(result["selection"]["split_counts"], {"train": 2})
            self.assertEqual(result["s04_tempo_vs_microtiming"]["fixed_tempo_map_sequences"], 2)
            self.assertEqual(
                result["s04_tempo_vs_microtiming"]
                ["fixed_tempo_with_mean_absolute_sixteenth_residual_at_least_2_ticks"],
                2,
            )


if __name__ == "__main__":
    unittest.main()
