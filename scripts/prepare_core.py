"""Prepare local core artifacts: data generation and initial model training.

Task 4: Before reusing any cached model, validate:
- source dataset == synthetic
- architecture_id matches current ARCHITECTURE_ID (neural only)
- feature_schema_hash matches current SCHEMA_HASH
- model artifact file exists on disk
- model_hash in metadata matches actual artifact bytes
- threshold, threshold_selection_metric, validation_score exist (neural only)
- model loads successfully (Predictor())

If any check fails, retrain that model and record retrained_due_to_<reason>.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + str(ROOT)


def run(*args: str) -> None:
    completed = subprocess.run([sys.executable, "-m", "nexora.cli", *args], cwd=ROOT, env=ENV)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def _validate_neural_model(kind: str) -> tuple[bool, str]:
    """Return (is_valid, reason). reason is empty string if valid."""
    from nexora.features.extract import SCHEMA_HASH
    from nexora.ml.train import ARCHITECTURE_ID, Predictor

    meta_path = ROOT / f"models/synthetic/{kind}/metadata.json"
    if not meta_path.is_file():
        return False, "metadata_missing"

    try:
        meta = json.loads(meta_path.read_text())
    except Exception:
        return False, "metadata_unreadable"

    # source check
    if meta.get("source") not in ("synthetic", "Synthetic"):
        return False, f"wrong_source:{meta.get('source')}"

    if kind == "neural":
        # architecture_id check
        if meta.get("architecture_id") != ARCHITECTURE_ID:
            return False, f"architecture_mismatch:{meta.get('architecture_id')}"

        # feature_schema_hash check
        if meta.get("feature_schema_hash") != SCHEMA_HASH:
            return False, f"schema_hash_mismatch:{meta.get('feature_schema_hash')[:8] if meta.get('feature_schema_hash') else 'none'}"

        # threshold / validation_score required fields
        if "threshold" not in meta:
            return False, "threshold_missing"
        if "threshold_selection_metric" not in meta:
            return False, "threshold_selection_metric_missing"
        if "validation_score" not in meta:
            return False, "validation_score_missing"

    # artifact file exists
    if kind == "neural":
        artifact = ROOT / f"models/synthetic/{kind}/weights.safetensors"
    else:
        artifact = ROOT / f"models/synthetic/{kind}/weights.npz"

    if not artifact.is_file():
        return False, "artifact_missing"

    # model_hash matches actual bytes
    if "model_hash" in meta:
        actual_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if actual_hash != meta["model_hash"]:
            return False, f"hash_mismatch:stored={meta['model_hash'][:8]} actual={actual_hash[:8]}"

    # model loads successfully (neural only — baseline uses numpy)
    if kind == "neural":
        try:
            _p = Predictor()  # noqa: F841 — just checking it loads
        except Exception as exc:
            return False, f"load_failed:{exc}"

    return True, ""


def main():
    steps = []

    if not (ROOT / "data/synthetic/manifest.json").is_file():
        run("data", "generate", "--profile", "demo", "--seed", "42")
        steps.append("generated Synthetic data")
    else:
        steps.append("reused matching Synthetic data")

    for kind in ("baseline", "neural"):
        valid, reason = _validate_neural_model(kind)
        if valid:
            steps.append(f"reused_valid_model:{kind}")
        else:
            steps.append(f"retrained_due_to_{reason}:{kind}")
            run("train", kind, "--dataset", "synthetic")

    registry_active = ROOT / "models/registry/active.json"
    if not registry_active.exists() and (ROOT / "models/synthetic/neural/metadata.json").exists():
        registry_active.parent.mkdir(parents=True, exist_ok=True)
        meta = json.loads((ROOT / "models/synthetic/neural/metadata.json").read_text())
        meta['source'] = 'synthetic'
        meta['artifact_path'] = str(ROOT / "models/synthetic/neural")
        meta['lifecycle_state'] = 'active'
        registry_active.write_text(json.dumps(meta, indent=2))
        steps.append("activated synthetic neural model")

    print(json.dumps({"status": "core_prepared", "steps": steps}, indent=2))


if __name__ == "__main__":
    main()
