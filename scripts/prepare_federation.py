"""Prepare local federation artifacts: standard and private federated rounds.

Task 5: Before reusing a completed federation run, validate ALL of:
- dataset matches
- architecture_id matches current ARCHITECTURE_ID
- feature_schema_hash matches current SCHEMA_HASH
- protocol_version == 'nexora-fed-v1'
- status == 'completed'
- requested round count matches
- private/non-private mode matches

If any mismatch: run a new experiment.
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

PROTOCOL_VERSION = "nexora-fed-v1"
REQUIRED_ROUNDS = 1  # default: 1 round for each mode in demo prep


def run(*args: str) -> None:
    completed = subprocess.run([sys.executable, "-m", "nexora.cli", *args], cwd=ROOT, env=ENV)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def _is_reusable_run(manifest: dict, mode: str, dataset: str, rounds: int) -> tuple[bool, str]:
    """Return (reusable, rejection_reason). Task 5: strict validation."""
    from nexora.features.extract import SCHEMA_HASH
    from nexora.ml.train import ARCHITECTURE_ID

    if manifest.get("status") != "completed":
        return False, f"status:{manifest.get('status')}"
    if manifest.get("mode") != mode:
        return False, f"mode:{manifest.get('mode')}"
    if manifest.get("dataset") != dataset:
        return False, f"dataset:{manifest.get('dataset')}"
    if manifest.get("architecture_id") != ARCHITECTURE_ID:
        return False, f"architecture_id:{manifest.get('architecture_id')}"
    if manifest.get("feature_schema_hash") != SCHEMA_HASH:
        return False, f"feature_schema_hash:{str(manifest.get('feature_schema_hash'))[:8]}"
    if manifest.get("protocol_version") != PROTOCOL_VERSION:
        return False, f"protocol_version:{manifest.get('protocol_version')}"
    if len(manifest.get("rounds", [])) != rounds:
        return False, f"round_count:{len(manifest.get('rounds', []))}!={rounds}"
        
    ds_meta_path = ROOT / "data" / dataset / "manifest.json"
    if not ds_meta_path.exists():
        return False, "dataset_manifest_missing"
    ds_hash = json.loads(ds_meta_path.read_text()).get("windows_sha256")
    if manifest.get("dataset_hash") != ds_hash:
        return False, f"dataset_hash_mismatch:{manifest.get('dataset_hash')}"
        
    if not manifest.get("base_model_hash"):
        return False, "base_model_hash_missing"
        
    run_id = manifest.get("run_id")
    if not run_id:
        return False, "run_id_missing"
        
    run_dir = ROOT / "artifacts" / "runs" / run_id
    base_model = run_dir / "round-0.safetensors"
    if not base_model.exists():
        return False, "round-0_missing"
    if hashlib.sha256(base_model.read_bytes()).hexdigest() != manifest["base_model_hash"]:
        return False, "round-0_hash_mismatch"
        
    if "model_hash" not in manifest:
        return False, "final_model_hash_missing"
    
    final_model = run_dir / f"round-{rounds}.safetensors"
    if not final_model.exists():
        return False, "final_round_missing"
    if hashlib.sha256(final_model.read_bytes()).hexdigest() != manifest["model_hash"]:
        return False, "final_round_hash_mismatch"
    
    return True, ""


def main():
    steps = []

    manifests = []
    for path in (ROOT / "artifacts/runs").glob("*/manifest.json"):
        try:
            manifests.append(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError):
            pass

    dataset = "synthetic"
    for mode in ("federated", "private-federated"):
        # Task 5: Check if any existing run fully matches all required criteria
        reusable = None
        rejection_reason = None
        for m in manifests:
            ok, reason = _is_reusable_run(m, mode, dataset, REQUIRED_ROUNDS)
            if ok:
                reusable = m
                break
            else:
                rejection_reason = reason  # keep last rejection reason for logging

        if reusable:
            steps.append(f"reused_valid_{mode}_run:{reusable.get('run_id', '?')[:8]}")
        else:
            steps.append(f"ran_{mode}:reason={rejection_reason or 'no_existing_run'}")
            run("experiment", "run", "--mode", mode, "--dataset", dataset, "--rounds", str(REQUIRED_ROUNDS))

    print(json.dumps({"status": "federation_prepared", "steps": steps}, indent=2))


if __name__ == "__main__":
    main()
