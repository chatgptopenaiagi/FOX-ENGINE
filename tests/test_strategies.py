import unittest

from fox_engine.strategies import StrategyRegistry


class StrategyRegistryTests(unittest.TestCase):
    def test_all_animals_are_independent_complete_records(self):
        from fox_engine.contracts import validate_record

        registry = StrategyRegistry()
        self.assertEqual(
            {record["strategy_id"] for record in registry.list()},
            {"OWL", "FOX", "WOLF", "OCTOPUS", "TORTOISE", "EAGLE", "ANT", "BEAVER"},
        )
        for record in registry.list():
            with self.subTest(strategy=record["strategy_id"]):
                validate_record("strategy", record)
                self.assertIn(record["strategy_id"], {
                    item["strategy_id"] for item in registry.select(record["applicability_conditions"][0])
                })

    def test_registration_never_overwrites_or_aliases(self):
        registry = StrategyRegistry()
        custom = registry.get("OWL")
        custom["strategy_id"] = "BADGER"
        custom["applicability_conditions"] = ["storage"]
        registry.register(custom)
        custom["description"] = "mutated externally"
        returned = registry.get("BADGER")
        self.assertNotEqual(returned["description"], custom["description"])
        returned["applicability_conditions"].clear()
        self.assertEqual(registry.get("BADGER")["applicability_conditions"], ["storage"])
        self.assertIn("BADGER", [item["strategy_id"] for item in registry.select("storage")])
        with self.assertRaises(ValueError):
            registry.register(registry.get("OWL"))

    def test_bad_registration_and_unknown_identity(self):
        registry = StrategyRegistry(include_builtins=False)
        with self.assertRaises(ValueError):
            registry.register({"strategy_id": "INCOMPLETE"})
        with self.assertRaises(KeyError):
            registry.get("MISSING")
        self.assertEqual(registry.list(), [])

    def test_selection_is_explicit_deterministic_and_not_universal(self):
        registry = StrategyRegistry()
        self.assertEqual(
            [item["strategy_id"] for item in registry.select("unknown")],
            ["OWL", "TORTOISE"],
        )
        selected = registry.select("unknown", ["assumptions"])
        self.assertEqual([item["strategy_id"] for item in selected], ["FOX", "OWL", "TORTOISE"])
        self.assertEqual(selected, registry.select(" UNKNOWN ", ["ASSUMPTIONS"]))
        for domain, gaps in [("", []), ("failure", "assumptions"), ("failure", [None])]:
            with self.subTest(domain=domain, gaps=gaps), self.assertRaises(ValueError):
                registry.select(domain, gaps)


if __name__ == "__main__":
    unittest.main()
