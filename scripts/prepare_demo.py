"""Prepare cached local demo artifacts without repeating matched private work."""
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

steps = []
if not (ROOT / "data/synthetic/manifest.json").is_file():
    run("data", "generate", "--profile", "demo", "--seed", "42"); steps.append("generated Synthetic data")
else: steps.append("reused matching Synthetic data")
for kind in ("baseline", "neural"):
    if not (ROOT / f"models/{kind}/metadata.json").is_file():
        run("train", kind, "--dataset", "synthetic"); steps.append(f"trained {kind}")
    else: steps.append(f"reused cached {kind}")
manifests = []
for path in (ROOT / "artifacts/runs").glob("*/manifest.json"):
    try: manifests.append(json.loads(path.read_text()))
    except (OSError, json.JSONDecodeError): pass
for mode in ("federated", "private-federated"):
    if not any(item.get("mode") == mode and item.get("status") == "completed" for item in manifests):
        run("experiment", "run", "--mode", mode, "--dataset", "synthetic", "--rounds", "1"); steps.append(f"ran {mode}")
    else: steps.append(f"reused completed {mode}")
subprocess.run([sys.executable, "scripts/build_evidence.py"], cwd=ROOT, env=ENV, check=True)
print(json.dumps({"status": "prepared", "steps": steps}, indent=2))
