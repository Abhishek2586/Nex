"""Validated sample-weighted aggregation for compatible floating tensors."""
from collections.abc import Mapping
import hashlib
import numpy as np


def state_hash(state: Mapping[str, np.ndarray]) -> str:
    digest = hashlib.sha256()
    for key in sorted(state):
        value = np.asarray(state[key])
        digest.update(key.encode())
        digest.update(str(value.dtype).encode())
        digest.update(np.asarray(value.shape, dtype=np.int64).tobytes())
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def fedavg(updates: list[tuple[int, Mapping[str, np.ndarray]]]):
    if len(updates) != 3:
        raise ValueError("all three registered clients are required")
    counts = [item[0] for item in updates]
    if any(not isinstance(count, int) or count <= 0 for count in counts):
        raise ValueError("record counts must be positive integers")
    keys = set(updates[0][1])
    if any(set(state) != keys for _, state in updates):
        raise ValueError("parameter keys differ")
    result = {}
    total = sum(counts)
    for key in sorted(keys):
        template = np.asarray(updates[0][1][key])
        if not np.issubdtype(template.dtype, np.floating):
            raise ValueError(f"unexpected non-floating parameter: {key}")
        weighted = np.zeros(template.shape, dtype=np.float64)
        for count, state in updates:
            value = np.asarray(state[key])
            if value.shape != template.shape or value.dtype != template.dtype:
                raise ValueError(f"shape or dtype mismatch: {key}")
            if not np.isfinite(value).all():
                raise ValueError(f"non-finite parameter: {key}")
            weighted += count * value.astype(np.float64)
        result[key] = (weighted / total).astype(template.dtype)
    return result
