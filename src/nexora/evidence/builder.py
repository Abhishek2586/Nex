"""Canonical evidence package builder (Tasks 14, 15).

Single source of truth for building the NEXORA evidence ZIP.
Called by both scripts/build_evidence.py and GET /api/v1/evidence/export.

ALLOWLIST-based: only explicitly listed paths are included.
Excludes: tokens, .env, cert private keys, SQLite, raw WESAD, node_modules, .venv, DP RNG state.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import platform
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

# Allowlisted relative paths (from ROOT)
ALLOWLISTED_STATIC = [
    "README.md",
    "BUILD_STATUS.md",
    "ACCEPTANCE_REPORT.md",
    "KNOWN_LIMITATIONS.md",
    "SECURITY.md",
    "THIRD_PARTY_NOTICES.md",
    "requirements.lock.txt",
    "configs/claim_map.json",
    "configs/source_catalog.json",
    "configs/feature_schema.json",
    "docs/ARCHITECTURE.md",
    "docs/DATA_AND_MODEL_CARD.md",
    "docs/PRIVACY_AND_THREAT_MODEL.md",
    "docs/CLAIM_IMPLEMENTATION_MAP.md",
    "docs/EXPERIMENT_PROTOCOL.md",
    "docs/DEMO_SCRIPT.md",
    "docs/EXAM_QA.md",
    "docs/USER_GUIDE.md",
    "docs/FINAL_HANDOFF.md",
    "artifacts/reports/NEXORA_TECHNICAL_REPORT.md",
    "artifacts/reports/PERFORMANCE.md",
    "artifacts/reports/rollback_test_evidence.json",
    "artifacts/reports/coordinator-outage.json",
    "artifacts/reports/tls-verification.json",
    "artifacts/reports/fresh-clone.json",
    "artifacts/reports/e2e-run.json",
    "artifacts/reports/multi-seed.json",
    "artifacts/reports/performance.json",
    "reports/pytest.xml",
    "artifacts/demo/DEMO_SCRIPT.md",
    "data/synthetic/manifest.json",
    "models/synthetic/baseline/metadata.json",
    "models/synthetic/neural/metadata.json",
    "models/registry/active.json",
    "evidence/recorded/WESAD_EVALUATION.json",
]

# Allowlisted glob patterns (relative to ROOT)
ALLOWLISTED_GLOBS = [
    "artifacts/runs/*/manifest.json",
    "runtime/client-*/privacy.json",
]

# Never include (denylist takes precedence over allowlist)
DENYLIST_PATTERNS = [
    "tokens.json",
    ".env",
    ".key",
    ".pem",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "__pycache__",
    "node_modules",
    ".venv",
    "dp_rng_state",
    "NEXORA_PATENT_REVIEWER_HARDENING_PLAN.md",
    "PATENT_AGENT_REVIEW_NOTES.md",
]


def _get_git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def _is_denied(path: Path) -> bool:
    for part in path.parts:
        for pattern in DENYLIST_PATTERNS:
            if pattern.startswith("*"):
                if part.endswith(pattern[1:]):
                    return True
            elif pattern in part:
                return True
    return False


def build_evidence_package(root: Path, output_path: Path) -> dict[str, Any]:
    """Build an allowlist-based evidence ZIP. Returns the manifest dict."""
    root = root.resolve()

    # Collect candidate files
    candidates: set[Path] = set()
    for rel in ALLOWLISTED_STATIC:
        p = root / rel
        if p.is_file():
            candidates.add(p)

    for pattern in ALLOWLISTED_GLOBS:
        for p in root.glob(pattern):
            if p.is_file():
                candidates.add(p)

    # Apply denylist
    files = sorted(p for p in candidates if not _is_denied(p))

    # Build per-file checksums
    entries = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        entries.append({"path": rel, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})

    # Active model info
    active_hash = None
    architecture_id = None
    try:
        active = json.loads((root / "models/registry/active.json").read_text())
        active_hash = active.get("model_hash")
        architecture_id = active.get("architecture_id")
    except Exception:
        pass

    # Feature schema hash
    feature_schema_hash = None
    try:
        from nexora.features.extract import SCHEMA_HASH
        feature_schema_hash = SCHEMA_HASH
    except Exception:
        pass
        
    dataset_hash: str | None = None
    dataset_seed: int = 42
    dataset_source: str = "Synthetic"
    try:
        ds_manifest = json.loads((root / "data/synthetic/manifest.json").read_text())
        dataset_hash = ds_manifest.get("windows_sha256")
        dataset_seed = ds_manifest.get("seed", 42)
        dataset_source = ds_manifest.get("source", "Synthetic")
    except Exception: pass
    
    reload_state: str = "unknown"
    reload_error: Any = None
    loaded_model_hash: Any = None
    try:
        from nexora.edge.inference import get_reload_state
        state = get_reload_state()
        reload_state = str(state.get("reload_status") or "unknown")
        err = state.get("reload_error")
        reload_error = str(err) if err else None
        loaded_hash = state.get("loaded_model_hash")
        loaded_model_hash = str(loaded_hash) if loaded_hash else None
    except Exception: pass

    git_commit = _get_git_commit(root)

    # Node/npm versions
    node_version, npm_version = None, None
    try:
        node_version = subprocess.check_output(["node", "-v"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        pass
    try:
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        npm_version = subprocess.check_output([npm_cmd, "-v"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        pass

    manifest = {
        "bundle": "NEXORA synthetic research evidence",
        "git_commit": git_commit,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
        "node_version": node_version,
        "npm_version": npm_version,
        "protocol_version": "nexora-fed-v1",
        "dataset_hash": dataset_hash,
        "dataset_seed": dataset_seed,
        "dataset_source": dataset_source,
        "registry_model_hash": active_hash,
        "loaded_model_hash": loaded_model_hash,
        "reload_state": reload_state,
        "reload_error": reload_error,
        "active_model_hash": active_hash,
        "architecture_id": architecture_id,
        "feature_schema_hash": feature_schema_hash,
        "source_status": {
            "synthetic": "executed",
            "wesad": "COMPLETED — evaluation executed locally; raw dataset not in repo; evidence at evidence/recorded/WESAD_EVALUATION.json",
            "hardware": "NOT_BUILT",
            "cloud": "OUT_OF_SCOPE",
            "clinical": "NOT_PERFORMED",
        },
        "excludes": [
            "tokens", "certificates", "private keys", "raw recorded data",
            "DP RNG state", "virtual environments", "dependencies", "SQLite databases",
            "internal patent notes",
        ],
        "files": entries,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
        archive.writestr("export-manifest.json", json.dumps(manifest, indent=2))

    return manifest
