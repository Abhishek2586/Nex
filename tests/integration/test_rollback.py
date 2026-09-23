"""Integration test: full activation and rollback success path via API.

Exercises: establish model A → activate candidate B via API → verify active hash changed via API
→ rollback via API → verify active hash restored to A via API → Predictor inference on restored
model → record evidence JSON.
"""
import hashlib
import json
import os
import shutil
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient
import torch

from nexora.federation.coordinator import app
from nexora.ml.train import network, ARCHITECTURE_ID
from nexora.features.extract import SCHEMA_HASH

ROOT = Path(__file__).resolve().parents[2]

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def test_rollback_api_success_path(monkeypatch):
    """Full rollback success path using actual Coordinator API."""
    
    # We will run the coordinator logic in a temporary directory to avoid affecting real registry
    tmp = Path(tempfile.mkdtemp(prefix='nexora-rollback-test-'))
    
    # Mock ROOT in coordinator to use our temp directory
    import nexora.federation.coordinator as coord
    monkeypatch.setattr(coord, 'ROOT', tmp)
    
    # Set up tokens so we can authenticate
    token_dir = tmp / 'runtime' / 'control'
    token_dir.mkdir(parents=True, exist_ok=True)
    test_token = "test-coordinator-token"
    token_dir.joinpath("tokens.json").write_text(json.dumps({"coordinator": test_token}))
    headers = {"Authorization": f"Bearer {test_token}"}
    
    client = TestClient(app)
    
    try:
        # Create Model A
        model_a_dir = tmp / 'models' / 'synthetic' / 'neural'
        model_a_dir.mkdir(parents=True, exist_ok=True)
        model_a_weights = model_a_dir / 'weights.safetensors'
        
        from safetensors.torch import save_file
        model_a = network()
        torch.manual_seed(100)
        save_file(model_a.state_dict(), str(model_a_weights))
        hash_a = sha256_file(model_a_weights)
        
        registry_dir = tmp / 'models' / 'registry'
        registry_dir.mkdir(parents=True, exist_ok=True)
        
        meta_a = {
            'source': 'synthetic',
            'model_id': 'neural',
            'run_id': 'initial-run',
            'model_hash': hash_a,
            'feature_schema_hash': SCHEMA_HASH,
            'architecture_id': ARCHITECTURE_ID,
            'artifact_path': str(model_a_weights),
            'threshold': 0.5,
            'threshold_selection_metric': 'balanced_accuracy',
            'validation_score': 0.75,
            'activated_at': time.time(),
            'lifecycle_state': 'active'
        }
        (registry_dir / 'active.json').write_text(json.dumps(meta_a, indent=2))
        
        # Create valid Model B candidate (train with different seed)
        run_b_id = 'test-candidate-run-b'
        run_b_dir = tmp / 'artifacts' / 'runs' / run_b_id
        run_b_dir.mkdir(parents=True, exist_ok=True)
        weights_b = run_b_dir / 'round-1.safetensors'
        
        model_b = network()
        torch.manual_seed(200)
        # Give it a tiny gradient step to make it distinct but valid
        optimizer = torch.optim.SGD(model_b.parameters(), lr=0.1)
        bx = torch.randn(1, 12)
        by = torch.tensor([1])
        torch.nn.functional.cross_entropy(model_b(bx), by).backward()
        optimizer.step()
        
        save_file(model_b.state_dict(), str(weights_b))
        hash_b = sha256_file(weights_b)
        
        assert hash_a != hash_b, "Models A and B must be distinct"
        
        manifest_b = {
            'run_id': run_b_id,
            'mode': 'federated',
            'dataset': 'synthetic',
            'feature_schema_hash': SCHEMA_HASH,
            'architecture_id': ARCHITECTURE_ID,
            'threshold': 0.6,
            'validation_score': 0.8,
            'rounds': [{'round': 1, 'model_hash': hash_b, 'metrics': {}}],
            'status': 'completed',
        }
        (run_b_dir / 'manifest.json').write_text(json.dumps(manifest_b, indent=2))
        
        # Step 4: POST actual activation endpoint
        resp = client.post(f"/api/v1/models/{run_b_id}/activate", headers=headers, json={"round": 1})
        assert resp.status_code == 200, f"Activation failed: {resp.text}"
        
        # Step 5: GET actual active endpoint
        resp = client.get("/api/v1/models/active")
        assert resp.status_code == 200
        active_b = resp.json()
        
        # Step 6: assert active hash == B
        assert active_b['model_hash'] == hash_b
        
        # Step 7 & 8: construct Predictor and run inference successfully on B
        # Predictor reads from 'models/registry/active.json' relative to its own execution context.
        # We need to temporarily set the CWD or patch Predictor to use our tmp registry
        old_cwd = os.getcwd()
        os.chdir(tmp)
        try:
            from nexora.ml.train import Predictor
            predictor_b = Predictor()
            import numpy as np
            probs_b = predictor_b.predict(np.zeros(12))[0]
            assert probs_b.shape == (2,)
        finally:
            os.chdir(old_cwd)
            
        # Step 9: POST actual rollback endpoint
        resp = client.post("/api/v1/models/rollback", headers=headers)
        assert resp.status_code == 200, f"Rollback failed: {resp.text}"
        
        # Step 10 & 11: GET active, assert hash == A
        resp = client.get("/api/v1/models/active")
        assert resp.status_code == 200
        active_a = resp.json()
        assert active_a['model_hash'] == hash_a
        
        # Step 12 & 13: construct Predictor, run inference successfully on A
        os.chdir(tmp)
        try:
            predictor_a = Predictor()
            probs_a = predictor_a.predict(np.zeros(12))[0]
            assert probs_a.shape == (2,)
        finally:
            os.chdir(old_cwd)
            
        # Write evidence
        evidence = {
            'test': 'rollback_success_path_api',
            'hash_a': hash_a,
            'hash_b': hash_b,
            'active_after_activate_b': active_b['model_hash'],
            'active_after_rollback': active_a['model_hash'],
            'rollback_restored_a': active_a['model_hash'] == hash_a
        }
        evidence_path = ROOT / 'artifacts' / 'reports' / 'rollback_test_evidence.json'
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, indent=2))
        
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
