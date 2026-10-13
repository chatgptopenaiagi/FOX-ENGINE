"""Review exact staged blobs, without printing potential secret values.

Heuristic publication gate, not a proof of absence. Human/agent review of all
staged content and provenance is still required. Exit nonzero on any finding.
"""
import hashlib
import json
from pathlib import PurePosixPath
import re
import subprocess
import sys


def git(*args):
    return subprocess.check_output(["git", *args])


patterns = {
    "private-key": rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "github-token": rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b",
    "provider-key": rb"\bsk-[A-Za-z0-9_-]{20,}\b",
    "aws-key": rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "credential-url": rb"https?://[^\s/]+:[^\s/@]+@",
    "personal-home": rb"(?i)(?:[A-Z]:[\\/]Users[\\/](?!Public\b)[^\s\\/]+|/ho" + rb"me/[^\s/]+)",
}
blocked_parts = {".env", ".venv", ".local", "__pycache__", ".ssh", "node_modules"}
findings, inventory = [], []
for item in git("ls-files", "--stage", "-z").split(b"\0"):
    if not item:
        continue
    header, encoded_path = item.split(b"\t", 1)
    mode, oid, stage = header.decode("ascii").split()
    path = encoded_path.decode("utf-8")
    blob = git("cat-file", "blob", oid)
    inventory.append({"path": path, "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()})
    if mode != "100644" or stage != "0":
        findings.append({"path": path, "rule": "non-regular-or-unmerged"})
    if blocked_parts.intersection(PurePosixPath(path).parts) or path.endswith((".pem", ".key", ".pfx")):
        findings.append({"path": path, "rule": "sensitive-or-generated-path"})
    try:
        blob.decode("utf-8")
    except UnicodeDecodeError:
        findings.append({"path": path, "rule": "unreviewed-binary"})
    for label, pattern in patterns.items():
        if re.search(pattern, blob):
            findings.append({"path": path, "rule": label})
    for match in re.findall(rb"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", blob):
        # Public action references include an @ followed by a digest, not email.
        if not match.endswith(b"@users.noreply.github.com") and not match.endswith(b"@example.invalid"):
            findings.append({"path": path, "rule": "email-review-required"})
print(json.dumps({"files": inventory, "findings": findings,
    "scope": "Exact staged blobs; heuristic scanning plus separate full content review required."}, indent=2))
sys.exit(bool(findings))
