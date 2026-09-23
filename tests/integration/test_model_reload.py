"""Integration test: model reload after activation / rollback.

Verifies that edge inference natively notices active model changes and reloads it dynamically.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path

import torch
from safetensors.torch import save_file

from nexora.ml.train import network, ARCHITECTURE_ID
from nexora.features.extract import SCHEMA_HASH
from nexora.edge import inference

ROOT = Path(__file__).resolve().parents[2]

def test_model_reload(monkeypatch):
    tmp = Path(tempfile.mkdtemp(prefix='nexora-reload-test-'))
    old_cwd = os.getcwd()
    
    try:
        os.chdir(tmp)
        
        # Setup registry and models
        registry_dir = tmp / 'models' / 'registry'
        registry_dir.mkdir(parents=True, exist_ok=True)
        active_path = registry_dir / 'active.json'
        
        model_a_dir = tmp / 'models' / 'synthetic' / 'neural'
        model_a_dir.mkdir(parents=True, exist_ok=True)
        weights_a = model_a_dir / 'weights.safetensors'
        
        model_b_dir = tmp / 'models' / 'synthetic' / 'neural_b'
        model_b_dir.mkdir(parents=True, exist_ok=True)
        weights_b = model_b_dir / 'weights.safetensors'
        
        torch.manual_seed(10)
        save_file(network().state_dict(), str(weights_a))
        torch.manual_seed(20)
        model_b = network()
        torch.nn.functional.cross_entropy(model_b(torch.randn(1, 12)), torch.tensor([1])).backward()
        torch.optim.SGD(model_b.parameters(), lr=0.1).step()
        save_file(model_b.state_dict(), str(weights_b))
        
        import hashlib
        hash_a = hashlib.sha256(weights_a.read_bytes()).hexdigest()
        hash_b = hashlib.sha256(weights_b.read_bytes()).hexdigest()
        
        meta_a = {
            'source': 'synthetic',
            'model_id': 'neural',
            'model_hash': hash_a,
            'feature_schema_hash': SCHEMA_HASH,
            'architecture_id': ARCHITECTURE_ID,
            'artifact_path': str(weights_a)
        }
        active_path.write_text(json.dumps(meta_a))
        
        # Reset inference module state
        inference._registry_path = active_path
        inference.predictor = None
        inference._last_active_hash = None
        
        # 1. get_predictor loads A
        pred = inference.get_predictor()
        assert pred is not None
        assert pred.metadata['model_hash'] == hash_a
        assert inference._last_active_hash == hash_a
        
        # 2. activate B
        meta_b = dict(meta_a)
        meta_b['model_hash'] = hash_b
        meta_b['artifact_path'] = str(weights_b)
        active_path.write_text(json.dumps(meta_b))
        
        # 3. get_predictor reloads B
        pred_b = inference.get_predictor()
        assert pred_b is not None
        assert pred_b.metadata['model_hash'] == hash_b
        assert pred_b is not pred # should be a new instance
        assert inference._last_active_hash == hash_b
        
        # 4. rollback A
        active_path.write_text(json.dumps(meta_a))
        
        # 5. get_predictor reloads A
        pred_a = inference.get_predictor()
        assert pred_a is not None
        assert pred_a.metadata['model_hash'] == hash_a
        assert pred_a is not pred_b # should be a new instance
        assert inference._last_active_hash == hash_a

    finally:
        os.chdir(old_cwd)
        shutil.rmtree(tmp, ignore_errors=True)
