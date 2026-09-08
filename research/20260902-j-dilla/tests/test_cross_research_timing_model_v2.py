import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "data" / "cross-research-timing-model-v2.json"


class CrossResearchTimingModelV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))

    def test_references_all_five_research_axes(self):
        axes = self.model["distinct_axes"]
        self.assertEqual(
            set(axes),
            {
                "j_dilla_clock_relation",
                "charlie_hunter_body_coupling",
                "jeff_mills_floor_and_break",
                "autechre_state_transition",
                "aphex_twin_identity_edit_horizon",
            },
        )

    def test_aphex_reference_is_remote_blob_anchored(self):
        refs = {item["research_id"]: item for item in self.model["retrieved_references"]}
        self.assertEqual(
            refs["20260902-aphex-twin"]["blob_sha"],
            "49e578cadfcd6d6ce4e3166279e8ae951cc3d9fb",
        )

    def test_recording_and_selection_remain_explicit(self):
        memory = self.model["time_field"]["identity_memory"]
        self.assertTrue(memory["explicit_recording_only"])
        self.assertFalse(memory["automatic_selection"])
        self.assertIn("automatic recording or playback after release", self.model["anti_patterns"])
        self.assertIn("automatic selection of the best take", self.model["anti_patterns"])

    def test_aphex_and_dilla_are_not_collapsed(self):
        rules = self.model["separation_rules"]
        self.assertTrue(any("recorded microtiming" in rule and "editing" in rule for rule in rules))

    def test_v2_preserves_original_six_operations_and_adds_four(self):
        names = [item["operation"] for item in self.model["performance_operations"]]
        self.assertEqual(
            names[:6],
            [
                "hold_floor",
                "bend_relation",
                "change_subdivision",
                "cut_layer",
                "recover_from_current_state",
                "release_to_floor",
            ],
        )
        self.assertEqual(
            names[6:],
            [
                "select_identity_anchor",
                "transform_local_detail",
                "commit_snapshot",
                "relisten_then_reenter",
            ],
        )


if __name__ == "__main__":
    unittest.main()
