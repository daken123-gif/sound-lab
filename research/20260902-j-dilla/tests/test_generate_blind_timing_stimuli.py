import hashlib
import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from generate_blind_timing_stimuli import generate_pack  # noqa: E402


class BlindTimingStimuliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.output = Path(self.temp.name)
        self.manifest, self.key = generate_pack(self.output)

    def tearDown(self):
        self.temp.cleanup()

    def test_two_anonymous_wavs_have_valid_headers(self):
        filenames = {item["filename"] for item in self.manifest["files"]}
        self.assertEqual(filenames, {"stimulus-A.wav", "stimulus-B.wav"})
        for filename in filenames:
            with wave.open(str(self.output / filename), "rb") as handle:
                self.assertEqual(handle.getnchannels(), 1)
                self.assertEqual(handle.getsampwidth(), 2)
                self.assertEqual(handle.getframerate(), 44_100)
                self.assertEqual(handle.getnframes(), 374_850)

    def test_conditions_have_same_content_count_but_different_audio(self):
        self.assertEqual(
            set(self.key["condition_to_file"]),
            {"global_swing", "structured_relation"},
        )
        hashes = {item["sha256"] for item in self.manifest["files"]}
        self.assertEqual(len(hashes), 2)
        rms_values = [item["rms_before_pcm_quantization"] for item in self.manifest["files"]]
        self.assertLess(max(rms_values) - min(rms_values), 1e-9)

    def test_public_manifest_does_not_reveal_assignment(self):
        public_text = (self.output / "blind-manifest.json").read_text(encoding="utf-8")
        self.assertNotIn("global_swing", public_text)
        self.assertNotIn("structured_relation", public_text)
        self.assertIn("global_swing", (self.output / "condition-key.json").read_text(encoding="utf-8"))

    def test_manifest_hashes_match_written_files(self):
        for item in self.manifest["files"]:
            digest = hashlib.sha256((self.output / item["filename"]).read_bytes()).hexdigest()
            self.assertEqual(digest, item["sha256"])

    def test_generation_is_reproducible_for_fixed_seed(self):
        with tempfile.TemporaryDirectory() as second_directory:
            second = Path(second_directory)
            manifest, key = generate_pack(second)
            self.assertEqual(manifest, self.manifest)
            self.assertEqual(key, self.key)
            for item in manifest["files"]:
                self.assertEqual(
                    (second / item["filename"]).read_bytes(),
                    (self.output / item["filename"]).read_bytes(),
                )

    def test_protocol_requires_locked_response_before_key(self):
        protocol = json.loads(
            (ROOT / "data" / "synthetic-blind-listening-protocol-v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(protocol["response_lock"], "required_before_condition_key")
        self.assertNotIn("dilla_likeness", protocol["rating_dimensions"])


if __name__ == "__main__":
    unittest.main()
