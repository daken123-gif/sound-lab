import unittest

from rwc_period_pilot import relate_candidates


class RwcPeriodPilotTest(unittest.TestCase):
    def test_direct_and_half_time_candidates_are_retained(self):
        candidates = [{"period": 1.0}, {"period": 0.5}, {"period": 0.73}]
        result = relate_candidates(candidates, 0.5)
        self.assertEqual(result["direct_match_rank"], 2)
        self.assertEqual(
            [row["nearest_meter_ratio"] for row in result["meter_related_candidates"]],
            [2.0, 1.0],
        )

    def test_unrelated_candidates_do_not_count_as_matches(self):
        result = relate_candidates([{"period": 0.71}], 0.5)
        self.assertIsNone(result["direct_match_rank"])
        self.assertEqual(result["meter_related_candidates"], [])


if __name__ == "__main__":
    unittest.main()
