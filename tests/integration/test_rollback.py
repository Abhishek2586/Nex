"""Integration test: full activation and rollback success path.

Exercises: establish model A → activate candidate B → verify active hash changed
→ rollback → verify active hash restored to A → Predictor inference on restored
model → record evidence JSON.

Does NOT start any server. Reproduces coordinator registry logic locally.
"""
import hashlib
import json
import os
import shutil
import tempfile
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _activate_run(registry_dir, run_id, round_number, safetensor_path,
                  feature_schema_hash):
    """Reproduce coordinator activate_model registry logic."""
    manifest = json.loads((safetensor_path.parent / 'manifest.json').read_text())
    round_meta = manifest['rounds'][round_number - 1]
    b_hash = sha256_file(safetensor_path)
    assert b_hash == round_meta['model_hash'], 'Hash mismatch on activate'

    meta = {
        'source': manifest.get('dataset', 'synthetic'),
        'model_id': 'neural',
        'run_id': run_id,
        'round': round_number,
        'model_hash': round_meta['model_hash'],
        'feature_schema_hash': feature_schema_hash,
        'architecture_id': 'mlp-12-ln-32-16-2-v1',
        'artifact_path': str(safetensor_path),
        'metrics': round_meta.get('metrics', {}),
        'activated_at': time.time(),
    }

    active_path = registry_dir / 'active.json'
    if active_path.exists():
        history_path = registry_dir / 'history.json'
        history = json.loads(history_path.read_text()) if history_path.exists() else []
        history.append(json.loads(active_path.read_text()))
        history_path.write_text(json.dumps(history, indent=2))

    active_path.write_text(json.dumps(meta, indent=2))
    return meta


def _rollback(registry_dir):
    """Reproduce coordinator rollback_model registry logic."""
    active_path = registry_dir / 'active.json'
    history_path = registry_dir / 'history.json'
    assert active_path.exists(), 'No active.json to rollback'
    assert history_path.exists(), 'No history.json to rollback from'
    history = json.loads(history_path.read_text())
    assert history, 'History is empty'
    previous = history.pop()
    active_path.write_text(json.dumps(previous, indent=2))
    history_path.write_text(json.dumps(history, indent=2))
    return previous


def test_rollback_success_path():
    """Full rollback success path:
    A → activate B → verify hash changed → rollback → verify hash restored to A
    → Predictor inference succeeds on restored model.
    """
    from nexora.features.extract import SCHEMA_HASH

    model_a_weights = ROOT / 'models' / 'synthetic' / 'neural' / 'weights.safetensors'
    model_a_meta_path = ROOT / 'models' / 'synthetic' / 'neural' / 'metadata.json'
    if not model_a_weights.exists():
        pytest.skip('No trained model (models/synthetic/neural/weights.safetensors missing)')

    model_a_meta = json.loads(model_a_meta_path.read_text())
    hash_a = model_a_meta['model_hash']

    tmp = Path(tempfile.mkdtemp(prefix='nexora-rollback-test-'))
    old_cwd = os.getcwd()
    try:
        registry_dir = tmp / 'registry'
        registry_dir.mkdir()

        # Set model A as current active
        meta_a = {
            'source': 'Synthetic',
            'model_id': 'neural',
            'run_id': 'model-a-baseline',
            'model_hash': hash_a,
            'feature_schema_hash': SCHEMA_HASH,
            'architecture_id': 'mlp-12-ln-32-16-2-v1',
            'artifact_path': str(model_a_weights),
            'threshold': model_a_meta.get('threshold', 0.5),
            'metrics': model_a_meta.get('metrics', {}),
            'activated_at': time.time(),
        }
        (registry_dir / 'active.json').write_text(json.dumps(meta_a, indent=2))

        # Create model B: copy weights + append a null byte to make distinct hash
        run_b_id = 'fake-run-b-for-rollback-test'
        run_b_dir = tmp / 'runs' / run_b_id
        run_b_dir.mkdir(parents=True)
        weights_b = run_b_dir / 'round-1.safetensors'
        weights_b.write_bytes(model_a_weights.read_bytes() + b'\x00')
        hash_b = sha256_file(weights_b)

        assert hash_a != hash_b, 'Models A and B must be distinct for this test'

        manifest_b = {
            'run_id': run_b_id,
            'mode': 'federated',
            'dataset': 'synthetic',
            'feature_schema_hash': SCHEMA_HASH,
            'rounds': [{'round': 1, 'model_hash': hash_b, 'metrics': {}}],
            'status': 'completed',
        }
        (run_b_dir / 'manifest.json').write_text(json.dumps(manifest_b, indent=2))

        # Activate model B
        meta_b = _activate_run(registry_dir, run_b_id, 1, weights_b, SCHEMA_HASH)
        active_after_b = json.loads((registry_dir / 'active.json').read_text())
        assert active_after_b['model_hash'] == hash_b, (
            f'After activating B, expected {hash_b!r}, got {active_after_b["model_hash"]!r}'
        )

        # Rollback to A
        _rollback(registry_dir)
        active_after_rollback = json.loads((registry_dir / 'active.json').read_text())
        assert active_after_rollback['model_hash'] == hash_a, (
            f'After rollback, expected {hash_a!r}, got {active_after_rollback["model_hash"]!r}'
        )

        # Construct Predictor from restored registry and run inference
        registry_dst = tmp / 'models' / 'registry'
        registry_dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(registry_dir / 'active.json', registry_dst / 'active.json')

        os.chdir(tmp)
        from nexora.ml.train import Predictor
        predictor = Predictor()
        import numpy as np
        dummy_features = [0.0] * 12
        result = predictor.predict(dummy_features)
        probs = result[0]
        assert probs.shape == (2,), f'Expected 2-class output, got {probs.shape}'
        assert abs(float(probs.sum()) - 1.0) < 1e-4, f'Probs do not sum to 1: {probs}'
        predicted_class = int(probs.argmax())

        # Write evidence
        evidence = {
            'test': 'rollback_success_path',
            'hash_a': hash_a,
            'hash_b': hash_b,
            'active_after_activate_b': active_after_b['model_hash'],
            'active_after_rollback': active_after_rollback['model_hash'],
            'rollback_restored_a': active_after_rollback['model_hash'] == hash_a,
            'inference_predicted_class': predicted_class,
            'inference_probabilities': [float(x) for x in probs],
        }
        evidence_path = ROOT / 'artifacts' / 'reports' / 'rollback_test_evidence.json'
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, indent=2))

    finally:
        os.chdir(old_cwd)
        shutil.rmtree(tmp, ignore_errors=True)
