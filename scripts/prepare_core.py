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

    # feature_schema_hash check for both
    if meta.get("feature_schema_hash") != SCHEMA_HASH:
        return False, f"schema_hash_mismatch:{meta.get('feature_schema_hash')[:8] if meta.get('feature_schema_hash') else 'none'}"

    # dataset hash checking for both
    dataset_manifest = ROOT / 'data' / 'synthetic' / 'manifest.json'
    if not dataset_manifest.exists():
        return False, "dataset_manifest_missing"
    ds_meta = json.loads(dataset_manifest.read_text())
    if meta.get("dataset_hash") != ds_meta.get("windows_sha256"):
        return False, "dataset_hash_mismatch"

    if kind == "neural":
        # architecture_id check
        if meta.get("architecture_id") != ARCHITECTURE_ID:
            return False, f"architecture_mismatch:{meta.get('architecture_id')}"

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
    if "model_hash" not in meta:
        return False, "model_hash_missing"
        
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

    # Validate dataset reuse strictly
    dataset_valid = False
    dataset_reason = "missing"
    data_manifest = ROOT / "data/synthetic/manifest.json"
    data_npz = ROOT / "data/synthetic/windows.npz"
    if data_manifest.is_file() and data_npz.is_file():
        try:
            m = json.loads(data_manifest.read_text())
            if m.get("source") != "Synthetic":
                dataset_reason = "wrong_source"
            elif m.get("seed") != 42:
                dataset_reason = "wrong_seed"
            elif m.get("sample_hz") != 4:
                dataset_reason = "wrong_sample_hz"
            elif m.get("subject_count") != 24:
                dataset_reason = "wrong_subject_count"
            elif len(m.get("splits", {}).get("train", [])) != 15 or len(m.get("splits", {}).get("validation", [])) != 3 or len(m.get("splits", {}).get("test", [])) != 6:
                dataset_reason = "wrong_splits"
            elif not m.get("clients"):
                dataset_reason = "missing_clients"
            elif any(c not in m.get("clients", {}) for c in ("client-a", "client-b", "client-c")) or any(not m["clients"][c] for c in ("client-a", "client-b", "client-c")):
                dataset_reason = "invalid_client_partitions"
            elif m.get("windows_sha256") != hashlib.sha256(data_npz.read_bytes()).hexdigest():
                dataset_reason = "windows_sha256_mismatch"
            elif m.get("feature_schema_hash") != __import__("nexora.features.extract", fromlist=["SCHEMA_HASH"]).SCHEMA_HASH:
                dataset_reason = "feature_schema_hash_mismatch"
            elif any(not (ROOT / f"data/synthetic/subject-{i:03}.npz").is_file() for i in range(24)):
                dataset_reason = "missing_subject_files"
            else:
                dataset_valid = True
        except Exception as e:
            dataset_reason = f"read_error_{e}"

    if not dataset_valid:
        run("data", "generate", "--profile", "demo", "--seed", "42")
        steps.append(f"regenerated_due_to_{dataset_reason}")
    else:
        steps.append("reused_valid_synthetic_data")

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
        meta['dataset_hash'] = json.loads((ROOT / 'data/synthetic/manifest.json').read_text()).get('windows_sha256')
        registry_active.write_text(json.dumps(meta, indent=2))
        steps.append("activated synthetic neural model")

    print(json.dumps({"status": "core_prepared", "steps": steps}, indent=2))


if __name__ == "__main__":
    main()
