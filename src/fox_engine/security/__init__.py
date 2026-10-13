"""Fail-closed authority checks, not an operating-system sandbox.

The host supplies grants obtained through its own approval mechanism. A grant
is not proof that a human approved it. This module never executes operations.
Path checks reduce accidental escapes; they cannot eliminate filesystem races
between authorization and an operation performed by a different component.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import os
import re
import stat
from typing import Callable


class AuthorizationError(PermissionError):
    """The requested operation is outside the supplied authority."""


class Operation(str, Enum):
    ANALYZE = "ANALYZE"
    READ_EVIDENCE = "READ_EVIDENCE"
    WRITE_EVIDENCE = "WRITE_EVIDENCE"
    CREATE_FILE = "CREATE_FILE"
    MODIFY_FILE = "MODIFY_FILE"
    EXECUTE_TEST = "EXECUTE_TEST"
    CREATE_PROCESS = "CREATE_PROCESS"
    INSTALL_DEPENDENCY = "INSTALL_DEPENDENCY"
    READ_CREDENTIALS = "READ_CREDENTIALS"
    DELETE = "DELETE"
    MODIFY_SECURITY = "MODIFY_SECURITY"
    ADMINISTER_ACCOUNT = "ADMINISTER_ACCOUNT"
    PRIVILEGED_COMMAND = "PRIVILEGED_COMMAND"
    EXPOSE_NETWORK = "EXPOSE_NETWORK"
    PUBLISH = "PUBLISH"
    MODIFY_PROTECTED_INSTALLATION = "MODIFY_PROTECTED_INSTALLATION"


_READ_ONLY = {Operation.ANALYZE, Operation.READ_EVIDENCE}
_CONTROLLED = {
    Operation.WRITE_EVIDENCE, Operation.CREATE_FILE, Operation.MODIFY_FILE,
    Operation.EXECUTE_TEST, Operation.CREATE_PROCESS, Operation.INSTALL_DEPENDENCY,
}
_RESERVED = {"CON", "PRN", "AUX", "NUL", "CLOCK$", "CONIN$", "CONOUT$"}
_RESERVED.update(f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10))
_SENSITIVE = {
    ".git", ".ssh", ".aws", ".azure", ".env", ".git-credentials",
    "id_rsa", "id_ed25519", "credentials", "credentials.json", "secrets.json",
}


def _timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise AuthorizationError("Grant timestamps must be ISO strings with a timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuthorizationError("Invalid grant timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AuthorizationError("Grant timestamps require a timezone")
    return parsed


@dataclass(frozen=True)
class Grant:
    """Host-issued exact operation/path/resource scope, valid in [start, end)."""

    grant_id: str
    operation: Operation
    path: str
    resource: str
    not_before: str
    expires_at: str

    def __post_init__(self) -> None:
        from fox_engine.contracts import validate_record
        for name in ("grant_id", "path", "resource"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise AuthorizationError(f"Grant {name} must be a nonempty string")
        try:
            object.__setattr__(self, "operation", Operation(self.operation))
        except (ValueError, TypeError) as exc:
            raise AuthorizationError("Unknown operation") from exc
        try:
            validate_record("authority", {
                "grant_id": self.grant_id, "operation": self.operation.value,
                "path": self.path, "resource": self.resource,
                "not_before": self.not_before, "expires_at": self.expires_at,
            })
        except ValueError as exc:
            raise AuthorizationError("Grant violates the authority contract") from exc
        if _timestamp(self.expires_at) <= _timestamp(self.not_before):
            raise AuthorizationError("Grant expiry must follow its start")


@dataclass(frozen=True)
class Permit:
    """An authorization snapshot; consumers must call require immediately."""

    _shield: AuthorityShield
    operation: Operation
    path: Path
    resource: str
    _grant: Grant | None

    def require(self, operation: Operation, path: str | Path, resource: str = "") -> None:
        """Recheck operation, scope, path and lifetime before an operation."""
        if operation != self.operation or resource != self.resource:
            raise AuthorizationError("Permit operation or resource mismatch")
        checked = self._shield._check(operation, path, resource, self._grant)
        if checked != self.path:
            raise AuthorizationError("Permit path mismatch")


class AuthorityShield:
    """Read-only defaults for one workspace, with explicit controlled grants.

    Symlinks and Windows reparse points inside the workspace are rejected,
    including links whose current target happens to be inside the workspace.
    This conservative concept implementation does not support network shares.
    Sensitive filenames are blocked heuristically, not a secret classifier.
    """

    def __init__(self, workspace: str | Path, *, clock: Callable[[], datetime] | None = None):
        self.workspace = Path(workspace).resolve(strict=True)
        if not self.workspace.is_dir():
            raise AuthorizationError("Workspace must be an existing directory")
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _path(self, value: str | Path) -> Path:
        if not isinstance(value, (str, Path)):
            raise AuthorizationError("Path must be a string or Path")
        raw = str(value)
        if not raw or "\x00" in raw or raw.startswith(("\\\\", "//")):
            raise AuthorizationError("Empty, device and network paths are unsupported")
        normalized = raw.replace("\\", "/")
        if re.match(r"^[A-Za-z]:/", normalized):
            if os.name != "nt":
                raise AuthorizationError("Foreign drive paths are unsupported")
            normalized = normalized[3:]
        elif ":" in normalized:
            raise AuthorizationError("Drive-relative paths and alternate streams are forbidden")
        parts = [part for part in normalized.split("/") if part]
        for part in parts:
            if part == ".." or (part != "." and part.rstrip(" .") != part):
                raise AuthorizationError("Traversal and ambiguous Windows paths are forbidden")
            if ":" in part or part.split(".")[0].upper() in _RESERVED:
                raise AuthorizationError("Device names and alternate streams are forbidden")
        candidate = Path(raw)
        if os.name != "nt" and "\\" in raw:
            raise AuthorizationError("Backslash paths are unsupported on this platform")
        if not candidate.is_absolute():
            candidate = self.workspace / candidate
        # Lexical containment must hold before following any filesystem links.
        try:
            relative = candidate.relative_to(self.workspace)
        except ValueError as exc:
            raise AuthorizationError("Path is outside the workspace") from exc
        cursor = self.workspace
        for part in relative.parts:
            lower = part.lower()
            if lower in _SENSITIVE or lower.startswith(".env."):
                raise AuthorizationError("Sensitive paths are unavailable to FOX operations")
            cursor = cursor / part
            try:
                info = cursor.lstat()
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise AuthorizationError("Cannot inspect the requested path") from exc
            if stat.S_ISLNK(info.st_mode) or (
                getattr(info, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
            ):
                raise AuthorizationError("Symlink and reparse-point paths are forbidden")
        try:
            resolved = candidate.resolve(strict=False)
            resolved.relative_to(self.workspace)
        except (ValueError, OSError, RuntimeError) as exc:
            raise AuthorizationError("Path cannot be resolved inside the workspace") from exc
        return resolved

    def _check(self, operation: Operation, path: str | Path, resource: str, grant: Grant | None) -> Path:
        try:
            operation = Operation(operation)
        except (ValueError, TypeError) as exc:
            raise AuthorizationError("Unknown operation") from exc
        if not isinstance(resource, str):
            raise AuthorizationError("Resource must be a string")
        if operation not in _READ_ONLY | _CONTROLLED:
            raise AuthorizationError("This operation is unavailable in the concept engine")
        resolved = self._path(path)
        if operation in _READ_ONLY:
            return resolved
        if not isinstance(grant, Grant):
            raise AuthorizationError("Controlled operation requires a host-issued grant")
        now = self._clock()
        if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
            raise AuthorizationError("Authority clock must return a timezone-aware datetime")
        if not (_timestamp(grant.not_before) <= now < _timestamp(grant.expires_at)):
            raise AuthorizationError("Grant is not currently valid")
        if operation != grant.operation or resource != grant.resource or self._path(grant.path) != resolved:
            raise AuthorizationError("Grant does not cover this exact operation, path and resource")
        return resolved

    def authorize(self, operation: Operation, path: str | Path, *, resource: str = "", grant: Grant | None = None) -> Permit:
        resolved = self._check(operation, path, resource, grant)
        return Permit(self, Operation(operation), resolved, resource, grant)


__all__ = ["AuthorityShield", "AuthorizationError", "Grant", "Operation", "Permit"]
