#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from generate_synthetic_benchmark import generate
from relational_fusion import build_graph, close_period


def node_at(graph: dict, period: float) -> dict:
    return next(node for node in graph["nodes"] if close_period(node["period"], period))


class RelationalFusionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name)
        generate(cls.output)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_s01_separates_pulse_and_accent_cycle_candidates(self) -> None:
        graph = build_graph(self.output / "s01.wav")
        self.assertIn("pulse_candidate", node_at(graph, 0.5)["roles"])
        self.assertIn("accent_cycle_candidate", node_at(graph, 1.0)["roles"])

    def test_s02_keeps_pulse_and_loop_cycle_with_rank_conflict(self) -> None:
        graph = build_graph(self.output / "s02.wav")
        self.assertIn("pulse_candidate", node_at(graph, 0.5)["roles"])
        cycle = node_at(graph, 2.0)
        self.assertIn("recurrence_cycle_candidate", cycle["roles"])
        self.assertTrue(any(row["type"] == "rank_disagreement" for row in cycle["conflicts"]))

    def test_s03_finds_layer_periods_and_joint_recurrence(self) -> None:
        graph = build_graph(self.output / "s03.wav")
        self.assertIn("layer_period_candidate", node_at(graph, 0.75)["roles"])
        self.assertIn("layer_period_candidate", node_at(graph, 1.0)["roles"])
        self.assertIn("joint_recurrence_candidate", node_at(graph, 3.0)["roles"])

    def test_s04_marks_time_varying_pulse(self) -> None:
        graph = build_graph(self.output / "s04.wav")
        self.assertTrue(graph["tempo_state"]["time_varying"])
        self.assertTrue(
            any("time_varying_pulse_candidate" in node["roles"] for node in graph["nodes"])
        )

    def test_zero_score_candidates_do_not_become_nodes(self) -> None:
        graph = build_graph(self.output / "s01.wav")
        scored_evidence = [
            row
            for node in graph["nodes"]
            for row in node["evidence"]
            if row["score"] is not None
        ]
        self.assertTrue(scored_evidence)
        self.assertTrue(all(row["score"] > 0.0 for row in scored_evidence))


if __name__ == "__main__":
    unittest.main()
