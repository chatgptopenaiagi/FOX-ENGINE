"""Compare revisable templates for a synthetic sensor-interface vision."""

import json

from fox_engine import FoxEngine
from fox_engine.architecture import discover_architectures


def run() -> dict:
    vision = "Explore software that identifies unfamiliar synthetic sensors and proposes bounded interface adapters."
    problem = {
        "problem_id": "synthetic-sensor-vision", "project_id": "synthetic-architecture-discovery",
        "description": vision, "domain": "architecture",
        "assumptions": ["Sensor discovery can be separated from adapter policy.", "Hardware behavior is not yet known."],
        "constraints": ["No hardware access is authorized.", "Competing proposals must remain revisable."],
        "desired_outcome": "Compare architecture candidates and specify observations needed before selecting one.",
    }
    return {
        "scenario": "synthetic-sensor-architecture", "synthetic": True,
        "decision": FoxEngine().analyze(problem),
        "discovery": discover_architectures(vision),
    }


if __name__ == "__main__":
    result = run()
    discovery = result["discovery"]
    print(json.dumps({
        "scenario": result["scenario"], "synthetic": True,
        "candidate_ids": [candidate["architecture_id"] for candidate in discovery["candidates"]],
        "comparison_dimensions": discovery["comparison_dimensions"],
        "generation_method": discovery["generation_method"],
        "verification_scope": discovery["verification_scope"],
        "execution_authority": discovery["execution_authority"],
        "strategy_ids": [strategy["strategy_id"] for strategy in result["decision"]["recommendations"]],
    }, sort_keys=True))
