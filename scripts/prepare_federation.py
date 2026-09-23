"""Prepare local federation artifacts: standard and private federated rounds."""
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
    
    manifests = []
    for path in (ROOT / "artifacts/runs").glob("*/manifest.json"):
        try: 
            manifests.append(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError): 
            pass
            
    for mode in ("federated", "private-federated"):
        if not any(item.get("mode") == mode and item.get("status") == "completed" for item in manifests):
            run("experiment", "run", "--mode", mode, "--dataset", "synthetic", "--rounds", "1")
            steps.append(f"ran {mode}")
        else: 
            steps.append(f"reused completed {mode}")

    print(json.dumps({"status": "federation_prepared", "steps": steps}, indent=2))

if __name__ == "__main__":
    main()
