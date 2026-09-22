"""Multi-seed training stability check.

Trains the neural model with multiple random seeds on the Synthetic dataset
and prints a markdown table of balanced accuracy results.

Usage (from repo root):
    python scripts/experiments/multi_seed_train.py
"""
import subprocess
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

seeds = [42, 123, 2026, 777]

python = sys.executable

print("| Run Type | Seed | Dataset | Balanced Accuracy |")
print("|---|---|---|---|")

for seed in seeds:
    res = subprocess.run(
        [python, "-m", "nexora.cli", "train", "neural", "--dataset", "synthetic", "--seed", str(seed)],
        capture_output=True, text=True, cwd=ROOT,
    )
    if res.returncode != 0:
        print(f"| Neural | {seed} | Synthetic | FAILED |", file=sys.stderr)
        continue
    try:
        out = json.loads(res.stdout)
        ba = out['metrics']['balanced_accuracy']
        print(f"| Neural | {seed} | Synthetic | {ba:.4f} |")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"| Neural | {seed} | Synthetic | PARSE_ERROR: {e} |", file=sys.stderr)
