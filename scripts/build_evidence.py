"""Build a checksum-indexed evidence ZIP without secrets or raw recordings.

Task 14: This script delegates to the canonical evidence builder in src/nexora/evidence/builder.py.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

OUTPUT = ROOT / "artifacts" / "reports" / "nexora-evidence.zip"


def build():
    from nexora.evidence.builder import build_evidence_package
    manifest = build_evidence_package(ROOT, OUTPUT)
    return OUTPUT, manifest


if __name__ == "__main__":
    output, manifest = build()
    sha256 = hashlib.sha256(output.read_bytes()).hexdigest()
    print(json.dumps({
        "path": str(output),
        "files": len(manifest["files"]),
        "sha256": sha256,
        "git_commit": manifest.get("git_commit"),
        "active_model_hash": manifest.get("active_model_hash"),
    }, indent=2))
