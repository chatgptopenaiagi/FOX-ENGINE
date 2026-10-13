"""Append-oriented evidence journals with independently checkable hash chains.

Hashes detect alterations relative to retained records; they do not prove truth,
authenticity, immutability, or prevent complete replacement/truncation by a writer.
Retain an external trusted final hash/count when rollback detection is required.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, BinaryIO, Mapping

from fox_engine.security import AuthorizationError, Operation, Permit


class EvidenceError(ValueError):
    """Evidence is malformed, duplicated, truncated, or inconsistent."""


_ZERO = "0" * 64
_FIELDS = {"format_version", "sequence", "previous_hash", "record", "record_hash", "entry_hash"}


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, UnicodeError) as exc:
        raise EvidenceError("Evidence must be finite UTF-8 JSON data") from exc


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _validate(record: Any) -> None:
    from fox_engine.contracts import validate_record
    try:
        validate_record("evidence", record)
    except ValueError as exc:
        raise EvidenceError(f"Invalid evidence record: {exc}") from exc


def _verify(data: bytes) -> tuple[list[dict[str, Any]], str]:
    records = []
    identities = set()
    previous = _ZERO
    if data and not data.endswith(b"\n"):
        raise EvidenceError("Incomplete journal line; preserve and investigate before appending")
    for sequence, line in enumerate(data.splitlines(), 1):
        try:
            entry = json.loads(line.decode("utf-8"), object_pairs_hook=_unique_object)
        except (ValueError, UnicodeError) as exc:
            raise EvidenceError(f"Invalid JSON on journal line {sequence}") from exc
        if not isinstance(entry, dict) or set(entry) != _FIELDS:
            raise EvidenceError(f"Invalid journal envelope on line {sequence}")
        if type(entry["format_version"]) is not int or entry["format_version"] != 1:
            raise EvidenceError("Unsupported journal format version")
        if type(entry["sequence"]) is not int or entry["sequence"] != sequence:
            raise EvidenceError("Journal sequence mismatch")
        if entry["previous_hash"] != previous:
            raise EvidenceError("Journal chain mismatch")
        record = entry["record"]
        _validate(record)
        if record["record_id"] in identities:
            raise EvidenceError("Duplicate evidence record identity")
        if entry["record_hash"] != _digest(record):
            raise EvidenceError("Evidence record hash mismatch")
        body = {key: value for key, value in entry.items() if key != "entry_hash"}
        if entry["entry_hash"] != _digest(body):
            raise EvidenceError("Journal entry hash mismatch")
        identities.add(record["record_id"])
        records.append(record)
        previous = entry["entry_hash"]
    return records, previous


def verify_journal(path: str | Path) -> list[dict[str, Any]]:
    """Read and verify every envelope, record contract, identity and chain link.

    Does not create files, repair data, execute reproduction commands, or check
    whether observations are true. A missing file raises FileNotFoundError.
    """
    return _verify(Path(path).read_bytes())[0]


def _lock(stream: BinaryIO) -> None:
    # Nonblocking advisory lock on the journal itself: no extra lock-file grant.
    if os.name == "nt":
        import msvcrt
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


class EvidenceJournal:
    """Single-writer journal. Append requires an explicit, live write permit.

    Example: shield.authorize(Operation.WRITE_EVIDENCE, path,
    resource='evidence-journal', grant=host_grant). Pass the resulting permit
    to append(record, permit=permit). A recommendation is never a grant.
    Parent directories must already exist. Locks are advisory; independent
    malicious writers and filesystem TOCTOU attacks require host isolation.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path).absolute()

    def verify(self) -> list[dict[str, Any]]:
        return verify_journal(self.path)

    def append(self, record: Mapping[str, Any], *, permit: Permit | None = None) -> str:
        if not isinstance(permit, Permit):
            raise AuthorizationError("Evidence append requires an explicit authority permit")
        permit.require(Operation.WRITE_EVIDENCE, self.path, "evidence-journal")
        # Round trip produces a detached JSON snapshot before validation/hashing.
        snapshot = json.loads(_canonical(record), object_pairs_hook=_unique_object)
        _validate(snapshot)
        # Use the authorized absolute path; authorization and IO must agree.
        with permit.path.open("a+b") as stream:
            try:
                _lock(stream)
            except OSError as exc:
                raise EvidenceError("Journal is unavailable for a single-writer append") from exc
            stream.seek(0)
            records, previous = _verify(stream.read())
            if any(item["record_id"] == snapshot["record_id"] for item in records):
                raise EvidenceError("Duplicate evidence record identity")
            entry = {
                "format_version": 1,
                "sequence": len(records) + 1,
                "previous_hash": previous,
                "record": snapshot,
                "record_hash": _digest(snapshot),
            }
            entry["entry_hash"] = _digest(entry)
            permit.require(Operation.WRITE_EVIDENCE, self.path, "evidence-journal")
            stream.seek(0, os.SEEK_END)
            stream.write(_canonical(entry) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
            return entry["entry_hash"]


__all__ = ["EvidenceJournal", "EvidenceError", "verify_journal"]
