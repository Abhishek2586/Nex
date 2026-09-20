"""Seeded correlated synthetic signals; hidden states are evaluation-only."""
import hashlib
import json
from pathlib import Path
import numpy as np
from nexora.features.extract import extract, SCHEMA_HASH

SCENARIOS = ["normal", "gradual_stress", "sustained_posture", "brief_posture", "missing_data", "high_motion", "repeated_dismissal"]

def generate_subject(subject, seed=42, seconds=600, scenario=None):
    rng = np.random.default_rng(np.random.SeedSequence([seed, subject]))
    n = seconds * 4
    t = np.arange(n) / 4
    labels = ((t // 120) % 2).astype(int)
    state = np.convolve(np.pad(labels.astype(float), (39, 0), mode="edge"), np.ones(40)/40, mode="valid")
    if scenario is not None:
        state = np.clip((t-30)/120, 0, 1) if scenario == "gradual_stress" else np.zeros(n)
    noise = rng.normal(0, .04, n)
    eda = 1.8 + rng.uniform(-.5, .5) + 1.1*state + .15*np.sin(t/17) + np.convolve(np.pad(noise, (7, 0), mode="edge"), np.ones(8)/8, mode="valid")
    temp = 32 + rng.uniform(-1, 1) - .45*state + .1*np.sin(t/43) + rng.normal(0, .025, n)
    acc = rng.normal(0, .015, (n, 3)) * (1 + state[:, None])
    acc[:, 2] += 1
    posture = np.full(n, 5.)
    if scenario in ("sustained_posture", "repeated_dismissal"):
        posture[t >= 10] = 28
    if scenario == "brief_posture":
        posture[(t >= 10) & (t < 15)] = 28
    if scenario == "high_motion":
        acc += rng.normal(0, .5, (n, 3))
    samples = np.column_stack([eda, temp, acc])
    if scenario == "missing_data":
        samples[(t >= 12) & (t < 40), 0] = np.nan
    return samples, labels, posture

def prepare(root=Path("data/synthetic"), seed=42):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    subjects = np.random.default_rng(seed).permutation(24).tolist()
    splits = {"train": subjects[:15], "validation": subjects[15:18], "test": subjects[18:]}
    manifest = {"source": "Synthetic", "seed": seed, "sample_hz": 4, "duration_s": 600, "splits": splits, "clients": {f"client-{c}": subjects[i*5:(i+1)*5] for i, c in enumerate("abc")}, "feature_schema_hash": SCHEMA_HASH}
    features, targets, ids = [], [], []
    for subject in range(24):
        samples, labels, posture = generate_subject(subject, seed)
        np.savez_compressed(root/f"subject-{subject:03}.npz", samples=samples, labels=labels, posture=posture)
        for start in range(0, len(samples), 120):
            y = labels[start:start+120]
            if len(np.unique(y)) != 1:
                continue
            result = extract(samples[start:start+120])
            if result["values"] is not None:
                features.append(result["values"]); targets.append(int(y[0])); ids.append(subject)
    np.savez_compressed(root/"windows.npz", x=np.array(features), y=np.array(targets), subjects=np.array(ids))
    manifest["windows_sha256"] = hashlib.sha256((root/"windows.npz").read_bytes()).hexdigest()
    (root/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
