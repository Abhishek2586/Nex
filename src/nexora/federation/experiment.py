"""Coordinator-owned launcher and evaluator for three isolated client processes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
import numpy as np
import torch
from safetensors.torch import load_file, save_file
from nexora.features.extract import normalize, SCHEMA_HASH
from nexora.federation.aggregate import fedavg, state_hash
from nexora.ml.train import network, evaluate


def _numpy_state(path: Path):
    return {key: tensor.detach().cpu().numpy() for key, tensor in load_file(str(path)).items()}


def run(rounds=5, private=False):
    run_id = str(uuid.uuid4())
    root = Path("artifacts/runs") / run_id
    root.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(42 if not private else int.from_bytes(os.urandom(8), "big"))
    model = network()
    base = root / "round-0.safetensors"
    save_file(model.state_dict(), str(base))
    history = []
    for round_number in range(1, rounds + 1):
        started = time.time()
        processes = []
        outputs = []
        for client in ["client-a", "client-b", "client-c"]:
            output = root / f"round-{round_number}-{client}.safetensors"
            command = [sys.executable, "-m", "nexora.federation.client_worker", "--client", client, "--base", str(base), "--output", str(output)]
            if private:
                command.append("--private")
            processes.append((client, subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)))
            outputs.append(output)
        client_meta = []
        for client, process in processes:
            stdout, stderr = process.communicate(timeout=180)
            if process.returncode:
                raise RuntimeError(f"{client} failed: {stderr[-1200:]}")
            client_meta.append(json.loads(stdout.strip().splitlines()[-1]))
        updates = [(meta["records"], _numpy_state(path)) for meta, path in zip(client_meta, outputs)]
        next_state = fedavg(updates)
        model.load_state_dict({key: torch.from_numpy(value) for key, value in next_state.items()})
        next_path = root / f"round-{round_number}.safetensors"
        save_file(model.state_dict(), str(next_path))
        history.append({
            "round": round_number,
            "status": "completed",
            "base_hash": hashlib.sha256(base.read_bytes()).hexdigest(),
            "model_hash": hashlib.sha256(next_path.read_bytes()).hexdigest(),
            "state_hash": state_hash(next_state),
            "clients": client_meta,
            "duration_s": time.time() - started,
        })
        base = next_path
    manifest = json.loads(Path("data/synthetic/manifest.json").read_text())
    with np.load("data/synthetic/windows.npz", allow_pickle=False) as data:
        mask = np.isin(data["subjects"], manifest["splits"]["test"])
        tx = torch.tensor(normalize(data["x"][mask]))
        with torch.no_grad():
            probabilities = model(tx).softmax(1).numpy()
        metrics = evaluate(data["y"][mask], probabilities)
    result = {
        "run_id": run_id,
        "mode": "private-federated" if private else "federated",
        "source": "Synthetic",
        "feature_schema_hash": SCHEMA_HASH,
        "rounds": history,
        "metrics": metrics,
        "privacy_scope": "example-level synthetic windows" if private else None,
        "status": "completed",
    }
    (root / "manifest.json").write_text(json.dumps(result, indent=2))
    return result
