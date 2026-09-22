"""One isolated local client's genuine MLP update."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
from safetensors.torch import load_file, save_file
from nexora.features.extract import normalize
from nexora.ml.train import network


def _load_partition(client_id: str):
    root = Path("data/synthetic")
    manifest = json.loads((root / "manifest.json").read_text())
    with np.load(root / "windows.npz", allow_pickle=False) as data:
        mask = np.isin(data["subjects"], manifest["clients"][client_id])
        x = normalize(data["x"][mask])
        y = data["y"][mask].astype(np.int64)

    return x, y


def _load_ledger(path: Path):
    if not path.exists():
        return {"history": [], "steps": 0, "epsilon": 0.0, "randomness_mode": "experimental_non_cryptographic"}
    return json.loads(path.read_text())


def train_client(client_id: str, base: Path, output: Path, private: bool):
    torch.set_num_threads(1)
    
    # Architecture check
    metadata_path = base.with_name('metadata.json')
    if metadata_path.exists():
        from nexora.ml.train import ARCHITECTURE_ID
        meta = json.loads(metadata_path.read_text())
        if meta.get('architecture_id') != ARCHITECTURE_ID:
            raise ValueError(f"Architecture mismatch in client. Expected {ARCHITECTURE_ID}, got {meta.get('architecture_id')}")
            
    model = network()
    model.load_state_dict(load_file(str(base)))
    x, y = _load_partition(client_id)
    dataset = torch.utils.data.TensorDataset(torch.tensor(x), torch.tensor(y))
    batch_size = min(32, len(dataset))
    generator = torch.Generator().manual_seed(4200 + ord(client_id[-1]))
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True, generator=generator)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    privacy = None
    ledger_path = Path("runtime") / client_id / "privacy.json"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger = _load_ledger(ledger_path)
    delta = min(1e-5, 1 / (100 * len(dataset)))
    noise = 1.2
    if private:
        from opacus import PrivacyEngine
        from opacus.accountants import RDPAccountant
        sample_rate = 1 / max(1, len(loader))
        projected = RDPAccountant()
        projected.history = [tuple(item) for item in ledger["history"]]
        for _ in range(len(loader)):
            projected.step(noise_multiplier=noise, sample_rate=sample_rate)
        if projected.get_epsilon(delta) > 8:
            raise RuntimeError("privacy budget guard would exceed epsilon 8")
        privacy = PrivacyEngine(accountant="rdp", secure_mode=False)
        privacy.accountant.history = [tuple(item) for item in ledger["history"]]
        model, optimizer, loader = privacy.make_private(
            module=model,
            optimizer=optimizer,
            data_loader=loader,
            noise_multiplier=noise,
            max_grad_norm=1.0,
            poisson_sampling=True,
        )
    model.train()
    steps = 0
    for bx, by in loader:
        optimizer.zero_grad()
        nn.functional.cross_entropy(model(bx), by).backward()
        optimizer.step()
        steps += 1
    if private:
        plain = model._module
        ledger = {
            "client_id": client_id,
            "privacy_unit": "one non-overlapping 30-second synthetic window",
            "accountant": "RDPAccountant",
            "history": [list(item) for item in privacy.accountant.history],
            "steps": ledger["steps"] + steps,
            "epsilon": float(privacy.get_epsilon(delta)),
            "delta": delta,
            "noise_multiplier": noise,
            "max_grad_norm": 1.0,
            "randomness_mode": "experimental_non_cryptographic",
            "dataset_identity": "synthetic-seed-42",
        }
        ledger_path.write_text(json.dumps(ledger, indent=2))
    else:
        plain = model
    save_file(plain.state_dict(), str(output))
    metadata = {"client_id": client_id, "records": len(dataset), "steps": steps, "private": private}
    if private:
        metadata["privacy"] = ledger
    output.with_suffix(".json").write_text(json.dumps(metadata, indent=2))
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True, choices=["client-a", "client-b", "client-c"])
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--private", action="store_true")
    args = parser.parse_args()
    print(json.dumps(train_client(args.client, args.base, args.output, args.private)))


if __name__ == "__main__":
    main()
