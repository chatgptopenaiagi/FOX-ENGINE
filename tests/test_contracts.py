from copy import deepcopy
import json
from pathlib import Path
import unittest
from fox_engine.contracts import SCHEMAS, ContractError, parse_json, validate_record
from fox_engine import FoxEngine
from test_core import problem, observation

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    Draft202012Validator = None


class ContractTests(unittest.TestCase):
    def test_closed_structures_and_real_json_types(self):
        for mutated in [{**problem(), "secret": "extra"}, {**problem(), "assumptions": "bad"},
                        {**problem(), "domain": "invented"}, {**problem(), "problem_id": "../escape"}]:
            with self.assertRaises(ContractError):
                validate_record("engineering_problem", mutated)
        for status in (True, "0", float("nan"), float("inf")):
            with self.assertRaises(ContractError):
                validate_record("evidence", {**observation(), "exit_status": status})

    def test_duplicate_keys_nonfinite_and_timestamp_validation(self):
        for text in ('{"a":1,"a":2}', '{"nested":{"x":0,"x":1}}', '{"a":NaN}'):
            with self.assertRaises(ValueError):
                parse_json(text)
        for timestamp in ("2026-01-01", "2026-01-01T00:00:00", "2026-02-30T00:00:00Z", "2026-01-01T00:00:00+00:60"):
            with self.assertRaises(ContractError):
                validate_record("evidence", {**observation(), "timestamp": timestamp})

    def test_exported_schema_drift(self):
        root = Path(__file__).resolve().parents[1] / "schemas"
        for name, schema in SCHEMAS.items():
            self.assertEqual(json.loads((root / f"{name}.schema.json").read_text(encoding="utf-8")), schema)

    @unittest.skipUnless(Draft202012Validator, "optional development jsonschema package unavailable")
    def test_independent_schema_validation_and_negative_parity(self):
        for schema in SCHEMAS.values():
            Draft202012Validator.check_schema(schema)
        fixtures = {"engineering_problem": problem(), "evidence": observation(),
                    "decision": FoxEngine().analyze(problem(), [observation()]),
                    "strategy": FoxEngine().registry.get("FOX")}
        for name, fixture in fixtures.items():
            validator = Draft202012Validator(SCHEMAS[name], format_checker=FormatChecker())
            validator.validate(fixture)
            for key in fixture:
                missing = deepcopy(fixture)
                del missing[key]
                self.assertFalse(validator.is_valid(missing), (name, key))
                with self.assertRaises(ContractError):
                    validate_record(name, missing)
        validator = Draft202012Validator(SCHEMAS["evidence"], format_checker=FormatChecker())
        for status in (0, 1.0, True, "0", None):
            record = {**observation(), "exit_status": status}
            expected = validator.is_valid(record)
            try:
                validate_record("evidence", record)
                accepted = True
            except ContractError:
                accepted = False
            self.assertEqual(accepted, expected)


if __name__ == "__main__":
    unittest.main()
