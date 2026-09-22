import subprocess
import json
from pathlib import Path
import sys

seeds = [42, 123, 2026, 777]

for seed in seeds:
    print(f"\n--- SEED {seed} ---")
    
    # 1. Regenerate synthetic data with the seed so dataset represents different initial state (wait, usually we keep the dataset stable and just change ML seed. The prompt said "Run multi-seed retrains", which implies model training seeds.)
    # Let's just run train neural with the seed. The dataset is currently generated with 42.
    # To be safe, I'll just change the ML seed.
    
    res = subprocess.run([sys.executable, "-m", "nexora.cli", "train", "neural", "--dataset", "synthetic", "--seed", str(seed)], capture_output=True, text=True, cwd="d:/Downloads/Nexora")
    if res.returncode != 0:
        print("Neural train failed:", res.stderr)
        continue
    out = json.loads(res.stdout)
    print(f"Neural (seed={seed}) Balanced Accuracy: {out['metrics']['balanced_accuracy']:.4f}")

    # For federation, experiment/run.py doesn't take a seed yet, but the underlying worker might.
    # The prompt mainly asks to run multi-seed retrains and perform final full verification. 
