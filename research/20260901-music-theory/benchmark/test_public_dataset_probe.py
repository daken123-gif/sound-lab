import csv
import io
import struct
import tempfile
import unittest
import wave
import zipfile
from pathlib import Path

from public_dataset_probe import (
    EGMD_COLUMNS,
    ProbeError,
    RWC_METADATA_COLUMNS,
    probe_egmd,
    probe_rwc_audio_zip,
    probe_rwc_annotations,
)


def write_csv(path, columns, rows, delimiter=","):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def midi_bytes():
    return b"MThd" + struct.pack(">IHHH", 6, 1, 1, 480) + b"MTrk\x00\x00\x00\x00"


def wav_bytes():
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b"\x00\x00\x00\x00" * 100)
    return output.getvalue()


class PublicDatasetProbeTest(unittest.TestCase):
    def test_egmd_metadata_and_midi_paths_are_joined(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            metadata = root / "e-gmd.csv"
            row = dict.fromkeys(EGMD_COLUMNS, "value")
            row.update(
                id="sequence-1",
                split="test",
                kit_name="Acoustic Kit",
                midi_filename="drummer1/sample.midi",
            )
            write_csv(metadata, EGMD_COLUMNS, [row])
            archive_path = root / "e-gmd-midi.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(
                    "e-gmd-v1.0.0/drummer1/sample.midi", midi_bytes()
                )
            with self.assertRaisesRegex(ProbeError, "split values differ"):
                probe_egmd(metadata, archive_path)

            rows = []
            for split in ("train", "validation", "test"):
                changed = row.copy()
                changed["id"] = split
                changed["split"] = split
                changed["midi_filename"] = f"drummer1/{split}.midi"
                rows.append(changed)
            write_csv(metadata, EGMD_COLUMNS, rows)
            with zipfile.ZipFile(archive_path, "w") as archive:
                for changed in rows:
                    archive.writestr(
                        "e-gmd-v1.0.0/" + changed["midi_filename"], midi_bytes()
                    )
            result = probe_egmd(metadata, archive_path)
            self.assertEqual(result["metadata"]["rows"], 3)
            self.assertEqual(result["midi_archive"]["midi_files_checked"], 3)
            self.assertEqual(result["audio"]["state"], "not_acquired")

    def test_egmd_rejects_missing_archive_member(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            metadata = root / "e-gmd.csv"
            rows = []
            for split in ("train", "validation", "test"):
                row = dict.fromkeys(EGMD_COLUMNS, "value")
                row.update(id=split, split=split, midi_filename=f"{split}.midi")
                rows.append(row)
            write_csv(metadata, EGMD_COLUMNS, rows)
            archive_path = root / "e-gmd-midi.zip"
            with zipfile.ZipFile(archive_path, "w"):
                pass
            with self.assertRaisesRegex(ProbeError, "misses 3 MIDI files"):
                probe_egmd(metadata, archive_path)

    def test_rwc_annotation_classes_are_validated(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            metadata_row = dict.fromkeys(RWC_METADATA_COLUMNS, "value")
            metadata_row.update(RWCID="RWC_P001", CollID="P")
            write_csv(root / "metadata.csv", RWC_METADATA_COLUMNS, [metadata_row], ";")
            base = root / "01_annotations_preprocessed"
            write_csv(base / "beats/RWC-P/RWC_P001.csv", ["t", "beat"], [
                {"t": "0.1", "beat": "1"}, {"t": "0.6", "beat": "2"}
            ], ";")
            write_csv(base / "chords/RWC-P/RWC_P001.csv", ["t_start", "t_end", "chord"], [
                {"t_start": "0.0", "t_end": "1.0", "chord": "C:maj"}
            ], ";")
            write_csv(base / "melody/RWC-P/RWC_P001.csv", ["t", "f0"], [
                {"t": "0.0", "f0": "0.0"}, {"t": "0.01", "f0": "440.0"}
            ], ";")
            midi_path = base / "MIDI_aligned/RWC-P/RWC_P001.mid"
            midi_path.parent.mkdir(parents=True)
            midi_path.write_bytes(midi_bytes())
            result = probe_rwc_annotations(root, "fixture-revision")
            self.assertEqual(result["metadata"]["unique_recording_ids"], 1)
            self.assertEqual(result["annotations"]["beat_files"], 1)
            self.assertEqual(result["audio"]["files_checked"], 0)

    def test_rwc_audio_is_joined_to_metadata_beats_and_midi(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            metadata_row = dict.fromkeys(RWC_METADATA_COLUMNS, "value")
            metadata_row.update(RWCID="RWC_R001", CollID="R")
            write_csv(root / "metadata.csv", RWC_METADATA_COLUMNS, [metadata_row], ";")
            base = root / "01_annotations_preprocessed"
            write_csv(base / "beats/RWC-R/RWC_R001.csv", ["t", "beat"], [
                {"t": "0.1", "beat": "1"}
            ], ";")
            midi_path = base / "MIDI_aligned/RWC-R/RWC_R001.mid"
            midi_path.parent.mkdir(parents=True)
            midi_path.write_bytes(midi_bytes())
            archive_path = root / "RWC-R.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("RWC-R/RWC_R001.wav", wav_bytes())
            import hashlib

            digest = hashlib.md5(
                archive_path.read_bytes(), usedforsecurity=False
            ).hexdigest()
            result = probe_rwc_audio_zip(archive_path, root, "R", digest)
            self.assertEqual(result["wav_files_checked"], 1)
            self.assertEqual(result["channels"], {"2": 1})
            self.assertTrue(
                all(value == 0 for value in result["annotation_join_missing_counts"].values())
            )


if __name__ == "__main__":
    unittest.main()
