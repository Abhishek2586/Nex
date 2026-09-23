"""Prepare local core artifacts: data generation and initial model training."""
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

def main():
    steps = []
    
    if not (ROOT / "data/synthetic/manifest.json").is_file():
        run("data", "generate", "--profile", "demo", "--seed", "42")
        steps.append("generated Synthetic data")
    else: 
        steps.append("reused matching Synthetic data")
        
    for kind in ("baseline", "neural"):
        if not (ROOT / f"models/synthetic/{kind}/metadata.json").is_file():
            run("train", kind, "--dataset", "synthetic")
            steps.append(f"trained {kind}")
        else: 
            steps.append(f"reused cached {kind}")
            
    registry_active = ROOT / "models/registry/active.json"
    if not registry_active.exists() and (ROOT / "models/synthetic/neural/metadata.json").exists():
        registry_active.parent.mkdir(parents=True, exist_ok=True)
        meta = json.loads((ROOT / "models/synthetic/neural/metadata.json").read_text())
        meta['source'] = 'synthetic'
        meta['artifact_path'] = str(ROOT / "models/synthetic/neural")
        # Ensure minimum metadata properties
        meta['lifecycle_state'] = 'active'
        registry_active.write_text(json.dumps(meta, indent=2))
        steps.append("activated synthetic neural model")
        
    print(json.dumps({"status": "core_prepared", "steps": steps}, indent=2))

if __name__ == "__main__":
    main()
