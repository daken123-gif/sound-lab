import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "validate_clock_relation_manifest.py"
SPEC = importlib.util.spec_from_file_location("validate_clock_relation_manifest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ManifestValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "data" / "clock-relation-manifest-v1.json"
        cls.manifest = json.loads(path.read_text(encoding="utf-8"))

    def test_repository_manifest_is_valid(self):
        self.assertEqual(MODULE.validate_manifest(self.manifest), [])

    def test_ready_requires_acquired_source(self):
        changed = copy.deepcopy(self.manifest)
        changed["recordings"][0]["analysis_status"] = "ready"
        errors = MODULE.validate_manifest(changed)
        self.assertTrue(any("cannot be ready before source acquisition" in e for e in errors))

    def test_acquired_requires_real_sha256(self):
        changed = copy.deepcopy(self.manifest)
        item = changed["recordings"][0]
        item.update(
            source_status="acquired",
            source_kind="full_length",
            rights_basis="user-owned local file",
            local_filename="runnin.wav",
            sha256="not-a-hash",
            duration_seconds=180.0,
            sample_rate_hz=44100,
            channels=2,
            file_size_bytes=123456,
        )
        errors = MODULE.validate_manifest(changed)
        self.assertTrue(any("lowercase 64-character hex" in e for e in errors))

    def test_region_must_have_sixteen_bars(self):
        changed = copy.deepcopy(self.manifest)
        changed["recordings"][0]["regions"] = [{
            "region_id": "r1",
            "start_seconds": 10.0,
            "end_seconds": 20.0,
            "start_bar": 1,
            "bar_count": 8,
            "alignment_note": "test",
        }]
        errors = MODULE.validate_manifest(changed)
        self.assertTrue(any("bar_count must be at least 16" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
