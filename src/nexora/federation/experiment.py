"""Coordinator-owned launcher and evaluator for three isolated client processes."""
import hashlib
import json
import os
from pathlib import Path
import time
import uuid
import httpx
import numpy as np
import torch
from safetensors.torch import load_file, save_file
from nexora.features.extract import normalize, SCHEMA_HASH
from nexora.federation.aggregate import fedavg, state_hash
from nexora.ml.train import network, evaluate, ARCHITECTURE_ID


def _numpy_state(path: Path):
    return {key: tensor.detach().cpu().numpy() for key, tensor in load_file(str(path)).items()}


def run(rounds=5, private=False, dataset="synthetic"):
    run_id = str(uuid.uuid4())
    root = Path("artifacts/runs") / run_id
    root.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(42 if not private else int.from_bytes(os.urandom(8), "big"))
    # Task 13: Federation explicitly uses random initialization as the round-0 base.
    # This trains a fresh global candidate rather than adapting the current active model.
    # Design choice: fresh random init for federation, documented in manifest as base_model_source.
    model = network()
    base = root / "round-0.safetensors"
    save_file(model.state_dict(), str(base))
    history = []
    for round_number in range(1, rounds + 1):
        started = time.time()
        client_urls = {
            "client-a": os.environ.get("NEXORA_CLIENT_A_URL", "http://127.0.0.1:8080") + "/api/v1/train",
            "client-b": os.environ.get("NEXORA_CLIENT_B_URL", "http://127.0.0.1:8082") + "/api/v1/train",
            "client-c": os.environ.get("NEXORA_CLIENT_C_URL", "http://127.0.0.1:8083") + "/api/v1/train"
        }
        
        ca_file = os.environ.get('NEXORA_CA_FILE')
        if ca_file:
            client_urls = {k: v.replace('http:', 'https:') for k, v in client_urls.items()}
        else:
            ca_file = True

        client_meta = []
        outputs = []
        
        token_path = Path('runtime/control/tokens.json')
        tokens = json.loads(token_path.read_text()) if token_path.exists() else {}
        
        with httpx.Client(verify=ca_file, timeout=180.0) as client:
            for c_id, url in client_urls.items():
                output = root / f"round-{round_number}-{c_id}.safetensors"
                headers = {'Authorization': f"Bearer {tokens.get(c_id, '')}"}
                base_hash = hashlib.sha256(base.read_bytes()).hexdigest()
                payload = {
                    'private': 'true' if private else 'false',
                    'dataset': dataset,
                    'run_id': run_id,
                    'round_id': str(round_number),
                    'base_model_hash': base_hash,
                    'feature_schema_hash': SCHEMA_HASH,
                    'architecture_id': ARCHITECTURE_ID,
                    'client_id': c_id,
                    'protocol_version': 'nexora-fed-v1'
                }
                
                with base.open('rb') as f:
                    resp = client.post(
                        url,
                        data=payload,
                        files={'base_model': (base.name, f, 'application/octet-stream')},
                        headers=headers
                    )
                if resp.status_code != 200:
                    raise RuntimeError(f"{c_id} failed: {resp.text}")
                
                output.write_bytes(resp.content)
                outputs.append(output)
                
                # Check for explicit errors instead of just missing headers
                if not resp.headers.get('X-Federation-Metadata'):
                    raise RuntimeError(f"{c_id} failed to return metadata. Raw response: {resp.text}")
                    
                client_meta.append(json.loads(resp.headers.get('X-Federation-Metadata', '{}')))

        base_state = _numpy_state(base)
        updates = []
        seen_clients = set()
        for expected_c_id, meta, path in zip(client_urls.keys(), client_meta, outputs):
            cid = meta.get("client_id")
            if cid in seen_clients:
                raise RuntimeError("Duplicate client ID detected")
            seen_clients.add(cid)
            # Validate response protocol metadata
            if meta.get("protocol_version") != "nexora-fed-v1": raise RuntimeError("Client update protocol_version mismatch")
            if meta.get("run_id") != run_id: raise RuntimeError("Client update run_id mismatch")
            if meta.get("round_id") != str(round_number): raise RuntimeError("Client update round_id mismatch")
            if meta.get("base_model_hash") != base_hash: raise RuntimeError("Client update base_model_hash mismatch")
            if meta.get("feature_schema_hash") != SCHEMA_HASH: raise RuntimeError("Client update feature_schema_hash mismatch")
            if meta.get("architecture_id") != ARCHITECTURE_ID: raise RuntimeError("Client update architecture_id mismatch")
            if meta.get("records", 0) <= 0: raise RuntimeError("Client update has no records")
            
            # Validation: check hashes and duplicates
            if meta.get("update_hash") != hashlib.sha256(path.read_bytes()).hexdigest():
                raise RuntimeError("Update hash mismatch")
                
            state = _numpy_state(path)
            # Validation: check shapes and hashes
            if state.keys() != base_state.keys():
                raise RuntimeError("Client update has mismatched keys")
            for k in state:
                if state[k].shape != base_state[k].shape:
                    raise RuntimeError(f"Client update shape mismatch on {k}")
                if state[k].dtype != base_state[k].dtype:
                    raise RuntimeError(f"Client update dtype mismatch on {k}")
                if not np.isfinite(state[k]).all():
                    raise RuntimeError(f"Client update contains non-finite values on {k}")
                    
            # Task 6 & 9: Verify update_hash matches actual received bytes (MANDATORY)
            if "update_hash" not in meta:
                raise RuntimeError("Update hash missing from client metadata")
            u_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if meta["update_hash"] != u_hash:
                raise RuntimeError(f"Update hash mismatch for {expected_c_id}: manifest={meta['update_hash'][:8]} actual={u_hash[:8]}")
            # Task 6: Verify response client_id matches the URL/identity we sent to
            if meta.get("client_id") != expected_c_id:
                raise RuntimeError(f"Client ID binding mismatch: sent to {expected_c_id} but response claims {meta.get('client_id')}")
            # Unique update hash check
            if any(h == u_hash for _, _, h in updates):
                raise RuntimeError("Duplicate update hash detected")

            updates.append((meta["records"], state, u_hash))

        # Check unique clients
        if len(set(meta.get("client_id") for meta in client_meta)) != len(client_meta):
            raise RuntimeError("Duplicate client ID detected")
            
        next_state = fedavg([(r, s) for r, s, _ in updates])
        model.load_state_dict({key: torch.from_numpy(value) for key, value in next_state.items()})
        next_path = root / f"round-{round_number}.safetensors"
        save_file(model.state_dict(), str(next_path))
        
        b_hash = hashlib.sha256(base.read_bytes()).hexdigest()
        m_hash = hashlib.sha256(next_path.read_bytes()).hexdigest()
        
        status = "completed"
        reason = None
        if b_hash == m_hash:
            status = "no_change"
            reason = "aggregate_identical_to_base"
            
        hist_item = {
            "round": round_number,
            "status": status,
            "base_hash": b_hash,
            "model_hash": m_hash,
            "state_hash": state_hash(next_state),
            "clients": client_meta,
            "duration_s": time.time() - started,
        }
        if reason:
            hist_item["reason"] = reason
        history.append(hist_item)
        base = next_path
        
    data_dir = Path("data/synthetic") if dataset == "synthetic" else Path(f"data/processed/{dataset}")
    manifest = json.loads((data_dir / "manifest.json").read_text())
    with np.load(data_dir / "windows.npz", allow_pickle=False) as data:
        val_mask = np.isin(data["subjects"], manifest["splits"]["validation"])
        test_mask = np.isin(data["subjects"], manifest["splits"]["test"])
        
        tx_val = torch.tensor(normalize(data["x"][val_mask]))
        tx_test = torch.tensor(normalize(data["x"][test_mask]))
        
        with torch.no_grad():
            val_probabilities = model(tx_val).softmax(1).numpy()
            test_probabilities = model(tx_test).softmax(1).numpy()
            
        # Threshold selection on validation split
        from sklearn.metrics import balanced_accuracy_score
        best_thresh = 0.5
        best_score = -1
        for t in np.linspace(0.1, 0.9, 81):
            t_pred = (val_probabilities[:, 1] > t).astype(int)
            score = balanced_accuracy_score(data["y"][val_mask], t_pred)
            if score > best_score:
                best_score = float(score)
                best_thresh = float(t)
                
        # Evaluate on test split using selected threshold
        metrics = evaluate(data["y"][test_mask], test_probabilities, threshold=best_thresh)
        metrics["threshold_used"] = best_thresh
        
    final_model_hash = hashlib.sha256(base.read_bytes()).hexdigest()
        
    result = {
        "run_id": run_id,
        "mode": "private-federated" if private else "federated",
        "source": "Synthetic" if dataset == "synthetic" else "Recorded dataset",
        "dataset": dataset,
        "feature_schema_hash": SCHEMA_HASH,
        "architecture_id": ARCHITECTURE_ID,
        "model_hash": final_model_hash,
        "rounds": history,
        "metrics": metrics,
        "threshold": best_thresh,
        "threshold_selection_metric": "balanced_accuracy",
        "validation_score": best_score,
        "validation_balanced_accuracy": best_score,
        "test_balanced_accuracy": metrics.get("balanced_accuracy"),
        "test_macro_f1": metrics.get("macro_f1"),
        "selected_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "privacy_scope": "example-level synthetic windows" if private else None,
        "status": "completed",
        "lifecycle_state": "candidate",
        "protocol_version": "nexora-fed-v1",
        "dataset_hash": manifest.get("windows_sha256"),
        "base_model_source": "random_init",
        "base_model_hash": hashlib.sha256((root / "round-0.safetensors").read_bytes()).hexdigest(),
        "base_model_architecture": ARCHITECTURE_ID,
        "base_model_note": "Federation trains a fresh global candidate from random initialization, not the current active model."
    }
    (root / "manifest.json").write_text(json.dumps(result, indent=2))
    return result
