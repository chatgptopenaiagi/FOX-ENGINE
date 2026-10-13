"""Run from the repository root with PYTHONPATH=src; --check is read-only."""
import argparse
import json
from pathlib import Path
from fox_engine.contracts import SCHEMAS

parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1] / "schemas"
for name, schema in SCHEMAS.items():
    path = root / f"{name}.schema.json"
    expected = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"schema drift: {path.name}")
    else:
        path.write_text(expected, encoding="utf-8")
print(f"{'Checked' if args.check else 'Exported'} {len(SCHEMAS)} schemas")
