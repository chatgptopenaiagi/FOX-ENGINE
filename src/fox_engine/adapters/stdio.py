"""One JSON request per input line; exactly one response per input line."""
from __future__ import annotations
import sys
from fox_engine.contracts import CONTRACT_VERSION, ContractError, canonical_json, parse_json, validate_record
from fox_engine.core import FoxEngine
from fox_engine.architecture import discover_architectures

MAX_LINE_BYTES = 1_048_576


def _fields(payload: dict, allowed: set[str], required: set[str]) -> None:
    if set(payload) - allowed or required - set(payload):
        raise ContractError("invalid operation payload fields")


def handle_request(request: dict) -> dict:
    request_id = None
    try:
        validate_record("request", request)
        request_id = request["request_id"]
        payload, operation = request["payload"], request["operation"]
        engine = FoxEngine()
        if operation == "analyze":
            _fields(payload, {"problem", "evidence", "hypotheses", "previous_decision"}, {"problem"})
            result = engine.analyze(**payload)
        elif operation == "strategies":
            _fields(payload, set(), set())
            result = engine.registry.list()
        elif operation == "discover_architecture":
            _fields(payload, {"vision", "candidates"}, {"vision"})
            result = discover_architectures(**payload)
        else:
            # Accept records, never an arbitrary filesystem path from an agent request.
            _fields(payload, {"records"}, {"records"})
            records = payload["records"]
            if type(records) is not list:
                raise ContractError("records must be an array")
            seen = set()
            for record in records:
                validate_record("evidence", record)
                if record["record_id"] in seen:
                    raise ContractError("duplicate evidence identity")
                seen.add(record["record_id"])
            result = {"status": "VERIFIED_CONCLUSION", "scope": "record structure and distinct identities only",
                      "count": len(records), "authenticity_verified": False}
        response = {"contract_version": CONTRACT_VERSION, "request_id": request_id, "ok": True, "result": result, "error": None}
    except (ValueError, TypeError, KeyError, RecursionError):
        # Do not echo rejected inputs, local paths, credentials or exception traces.
        response = {"contract_version": CONTRACT_VERSION, "request_id": request_id, "ok": False,
                    "result": None, "error": {"code": "INVALID_REQUEST", "message": "Request violates the FOX contract or operation requirements."}}
    validate_record("response", response)
    return response


def main() -> int:
    stream = sys.stdin.buffer
    failed = False
    while True:
        line = stream.readline(MAX_LINE_BYTES + 1)
        if not line:
            break
        oversize = len(line) > MAX_LINE_BYTES
        if oversize:
            while line and not line.endswith(b"\n"):
                line = stream.readline(MAX_LINE_BYTES + 1)
            request = None
        else:
            try:
                request = parse_json(line.decode("utf-8"))
            except (ValueError, UnicodeDecodeError, RecursionError):
                request = None
        response = handle_request(request)
        failed |= not response["ok"]
        sys.stdout.write(canonical_json(response) + "\n")
        sys.stdout.flush()
    return 1 if failed else 0
