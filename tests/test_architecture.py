from copy import deepcopy
import unittest

from fox_engine.architecture import COMPARISON_DIMENSIONS, discover_architectures


class ArchitectureDiscoveryTests(unittest.TestCase):
    def test_reproducible_complete_competing_proposals(self):
        vision = "Discover synthetic sensors through approved interfaces."
        result = discover_architectures(vision)
        self.assertEqual(result, discover_architectures(vision))
        self.assertEqual(result["vision"], vision)
        self.assertEqual(result["generation_method"], "DETERMINISTIC_TEMPLATES")
        self.assertEqual(result["execution_authority"], "NONE")
        self.assertGreaterEqual(len(result["candidates"]), 2)
        for candidate in result["candidates"]:
            self.assertEqual(candidate["epistemic_status"], "PROPOSAL")
            self.assertTrue(candidate["revisable"])
            self.assertEqual(set(candidate["comparison"]), set(COMPARISON_DIMENSIONS))

    def test_host_can_propose_without_mutating_input(self):
        candidates = discover_architectures("Synthetic vision")["candidates"]
        candidates[0]["name"] = "Domain-specific candidate"
        preserved = deepcopy(candidates)
        result = discover_architectures("Synthetic vision", candidates)
        self.assertEqual(result["generation_method"], "CALLER_PROPOSALS")
        result["candidates"][0]["assumptions"].clear()
        self.assertEqual(candidates, preserved)

    def test_incomplete_comparison_rejected_for_each_dimension(self):
        for dimension in COMPARISON_DIMENSIONS:
            candidates = discover_architectures("Synthetic vision")["candidates"]
            del candidates[0]["comparison"][dimension]
            with self.subTest(dimension=dimension), self.assertRaisesRegex(ValueError, "comparison"):
                discover_architectures("Synthetic vision", candidates)

    def test_broken_graph_rejected(self):
        candidates = discover_architectures("Synthetic vision")["candidates"]
        candidates[0]["dependencies"][0]["to_component"] = "undeclared"
        with self.assertRaisesRegex(ValueError, "declared component"):
            discover_architectures("Synthetic vision", candidates)

    def test_false_certainty_and_nonrevisable_candidates_rejected(self):
        for field, value in [("epistemic_status", "VERIFIED_CONCLUSION"), ("revisable", False)]:
            candidates = discover_architectures("Synthetic vision")["candidates"]
            candidates[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                discover_architectures("Synthetic vision", candidates)

    def test_invalid_vision_and_no_real_competition_rejected(self):
        with self.assertRaises(ValueError):
            discover_architectures(" ")
        candidates = discover_architectures("Synthetic vision")["candidates"]
        for proposed in [[], candidates[:1], [candidates[0], candidates[0]], "invalid"]:
            with self.subTest(candidates=proposed), self.assertRaises(ValueError):
                discover_architectures("Synthetic vision", proposed)


if __name__ == "__main__":
    unittest.main()
