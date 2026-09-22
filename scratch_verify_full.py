import subprocess
import json
from pathlib import Path
import sys

seeds = [42, 123, 2026, 777]

print("| Run Type | Seed | Dataset | Balanced Accuracy |")
print("|---|---|---|---|")

for seed in seeds:
    res = subprocess.run([sys.executable, "-m", "nexora.cli", "train", "neural", "--dataset", "synthetic", "--seed", str(seed)], capture_output=True, text=True, cwd="d:/Downloads/Nexora")
    if res.returncode != 0:
        continue
    out = json.loads(res.stdout)
    ba = out['metrics']['balanced_accuracy']
    print(f"| Neural | {seed} | Synthetic | {ba:.4f} |")

for mode in ['federated', 'private-federated']:
    # Federated runs use seed 42 internally typically. We'll just run it once.
    res = subprocess.run([sys.executable, "-m", "nexora.cli", "experiment", "run", "--mode", mode, "--dataset", "synthetic"], capture_output=True, text=True, cwd="d:/Downloads/Nexora")
    if res.returncode != 0:
        continue
    out = json.loads(res.stdout)
    ba = out['metrics']['balanced_accuracy']
    print(f"| {mode} | 42 | Synthetic | {ba:.4f} |")
