"""Build a checksum-indexed evidence ZIP without secrets or raw recordings."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "reports" / "nexora-evidence.zip"
STATIC = [
    "README.md", "BUILD_STATUS.md", "ACCEPTANCE_REPORT.md", "KNOWN_LIMITATIONS.md", "requirements.lock.txt",
    "configs/claim_map.json", "docs/ARCHITECTURE.md", "docs/DATA_AND_MODEL_CARD.md",
    "configs/source_catalog.json", "configs/feature_schema.json", "docs/PRIVACY_AND_THREAT_MODEL.md",
    "docs/CLAIM_IMPLEMENTATION_MAP.md", "docs/EXPERIMENT_PROTOCOL.md", "docs/DEMO_SCRIPT.md",
    "docs/EXAM_QA.md", "docs/USER_GUIDE.md", "docs/FINAL_HANDOFF.md",
    "artifacts/reports/NEXORA_TECHNICAL_REPORT.md", "artifacts/reports/NEXORA_TECHNICAL_REPORT.html",
    "artifacts/demo/DEMO_SCRIPT.md", "data/synthetic/manifest.json",
    "models/baseline/metadata.json", "models/neural/metadata.json",
    "artifacts/reports/coordinator-outage.json",
    "artifacts/reports/tls-verification.json",
]


def build():
    candidates = [ROOT / item for item in STATIC]
    candidates += list((ROOT / "artifacts" / "runs").glob("*/manifest.json"))
    candidates += list((ROOT / "runtime").glob("client-*/privacy.json"))
    files = sorted({path.resolve() for path in candidates if path.is_file()})
    entries = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        entries.append({"path": relative, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {
        "bundle": "NEXORA synthetic research evidence",
        "source_status": {"synthetic": "executed", "wesad": "unavailable"},
        "excludes": ["tokens", "certificates", "private keys", "raw recorded data", "DP RNG state", "virtual environments", "dependencies"],
        "files": entries,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr("export-manifest.json", json.dumps(manifest, indent=2))
    return OUTPUT, manifest


if __name__ == "__main__":
    output, manifest = build()
    print(json.dumps({"path": str(output), "files": len(manifest["files"]), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, indent=2))
