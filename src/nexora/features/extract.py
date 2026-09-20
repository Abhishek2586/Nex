"""Shared offline/online 30-second feature contract, sampled at 4 Hz."""
import hashlib
import json
import numpy as np

NAMES = ["eda_mean", "eda_std", "eda_slope", "eda_p95", "temperature_mean", "temperature_std", "temperature_slope", "magnitude_mean", "magnitude_std", "magnitude_p95", "magnitude_energy", "magnitude_change_rate"]
LOW = np.array([0, 0, -5, 0, 15, 0, -1, 0, 0, 0, 0, 0], dtype=float)
HIGH = np.array([50, 20, 5, 50, 45, 5, 1, 5, 3, 5, 16, 20], dtype=float)
SCHEMA_HASH = hashlib.sha256(json.dumps({"version": "1.0", "names": NAMES, "low": LOW.tolist(), "high": HIGH.tolist()}, sort_keys=True).encode()).hexdigest()

def normalize(values):
    return np.clip((np.asarray(values) - LOW) / (HIGH - LOW), 0, 1).astype(np.float32)

def extract(samples):
    """Rows are EDA uS, temperature degC, acceleration x/y/z in g.

    Missing samples must retain their slots on the canonical timeline. Repair only
    interior runs <=1 second; reject windows below 90% coverage or with long gaps.
    """
    x = np.asarray(samples, dtype=float).copy()
    if x.shape != (120, 5):
        return {"values": None, "reason": "incomplete_window", "repaired": 0}
    coverage = np.isfinite(x).mean(axis=0)
    if (coverage < .9).any():
        return {"values": None, "reason": "insufficient_coverage", "coverage": coverage.tolist(), "repaired": 0}
    repaired = 0
    for col in range(5):
        missing = np.flatnonzero(~np.isfinite(x[:, col]))
        for run in np.split(missing, np.where(np.diff(missing) != 1)[0] + 1):
            if not len(run):
                continue
            if len(run) > 4 or run[0] == 0 or run[-1] == 119:
                return {"values": None, "reason": "unrepairable_gap", "repaired": repaired}
            x[run, col] = np.interp(run, [run[0]-1, run[-1]+1], x[[run[0]-1, run[-1]+1], col])
            repaired += len(run)
    t = np.arange(120) / 4
    eda, temp = x[:, 0], x[:, 1]
    mag = np.linalg.norm(x[:, 2:5], axis=1)
    slope = lambda y: float(np.polyfit(t, y, 1)[0])
    values = [eda.mean(), eda.std(), slope(eda), np.percentile(eda, 95), temp.mean(), temp.std(), slope(temp), mag.mean(), mag.std(), np.percentile(mag, 95), np.mean((mag-1)**2), np.mean(np.abs(np.diff(mag))) * 4]
    return {"values": np.asarray(values).tolist(), "reason": None, "coverage": coverage.tolist(), "repaired": repaired, "schema_hash": SCHEMA_HASH}
