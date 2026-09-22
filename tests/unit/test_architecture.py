import pytest
import json
from pathlib import Path
from nexora.ml.train import Predictor, ARCHITECTURE_ID

def test_architecture_id_mismatch_rejected(tmp_path):
    # Create fake model metadata
    model_dir = tmp_path / 'models' / 'synthetic' / 'neural'
    model_dir.mkdir(parents=True)
    
    from nexora.features.extract import SCHEMA_HASH
    meta = {
        'model_id': 'neural',
        'architecture_id': 'invalid-arch-123',
        'feature_schema_hash': SCHEMA_HASH,
        'model_hash': 'fake-hash'
    }
    
    (model_dir / 'metadata.json').write_text(json.dumps(meta))
    
    # Fake weights
    (model_dir / 'weights.safetensors').write_bytes(b'fake-weights')
    
    import hashlib
    meta['model_hash'] = hashlib.sha256(b'fake-weights').hexdigest()
    (model_dir / 'metadata.json').write_text(json.dumps(meta))
    
    # Patch Path to use tmp_path
    import nexora.ml.train
    original_path = nexora.ml.train.Path
    class MockPath:
        def __new__(cls, *args, **kwargs):
            p = original_path(*args, **kwargs)
            if 'models' in p.parts:
                return tmp_path / p
            return p
            
    nexora.ml.train.Path = MockPath
    
    try:
        with pytest.raises(ValueError, match="Architecture mismatch"):
            Predictor(kind='neural', dataset='synthetic')
    finally:
        nexora.ml.train.Path = original_path
