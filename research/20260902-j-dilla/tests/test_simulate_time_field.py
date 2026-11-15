import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from simulate_time_field import (  # noqa: E402
    build_fixture,
    event_time,
    recover_from_current_state,
    release_to_floor,
)


class TimeFieldTests(unittest.TestCase):
    def test_global_swing_is_identical_across_voices(self):
        values = {
            voice: event_time(1, voice, 0.125, mode="global_swing", swing_seconds=0.02)
            for voice in ("kick", "snare", "hat")
        }
        self.assertEqual(len(set(values.values())), 1)

    def test_structured_relation_differs_across_voices(self):
        values = {
            voice: event_time(1, voice, 0.125, mode="structured_relation")
            for voice in ("kick", "snare", "hat")
        }
        self.assertEqual(len(set(values.values())), 3)

    def test_release_to_floor_changes_only_selected_voice(self):
        before = {"active_interventions": {"kick": -0.02, "snare": 0.015, "hat": 0.008}}
        after = release_to_floor(before, "snare")
        self.assertEqual(after["active_interventions"]["snare"], 0.0)
        self.assertEqual(after["active_interventions"]["kick"], -0.02)
        self.assertEqual(after["active_interventions"]["hat"], 0.008)
        self.assertEqual(before["active_interventions"]["snare"], 0.015)

    def test_recovery_never_rewinds(self):
        now = 1.37
        recovered = recover_from_current_state(now, target_phase=0.10, period=0.50)
        self.assertGreaterEqual(recovered, now)
        self.assertLess(recovered, now + 0.50)
        self.assertAlmostEqual(recovered, 1.60)

    def test_fixture_is_deterministic_and_json_serializable(self):
        first = json.dumps(build_fixture(), ensure_ascii=False, sort_keys=True)
        second = json.dumps(build_fixture(), ensure_ascii=False, sort_keys=True)
        self.assertEqual(first, second)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(first, encoding="utf-8")
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"],
                             "sound-lab.j-dilla.synthetic-time-field/v1")

    def test_repository_fixture_matches_generator(self):
        saved = json.loads((ROOT / "data" / "synthetic-time-field-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(saved, build_fixture())


if __name__ == "__main__":
    unittest.main()
