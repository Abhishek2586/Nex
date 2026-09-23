"""Integration tests for federation orchestration, identity binding, and rollback semantics."""
import hashlib
import json
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from nexora.federation.coordinator import app as coord_app
from nexora.edge.routes.federation import router as edge_router
from fastapi import FastAPI
from nexora.ml.train import ARCHITECTURE_ID
from nexora.features.extract import SCHEMA_HASH

ROOT = Path(__file__).resolve().parents[2]

edge_app = FastAPI()
edge_app.include_router(edge_router, prefix="/api/v1")

def test_client_identity_binding(monkeypatch):
    """Test that a client strictly requires matching identity token and URL mismatch raises an error."""
    tmp = Path(tempfile.mkdtemp())
    try:
        import nexora.edge.routes.federation as edge_fed
        monkeypatch.setattr(edge_fed, 'ROOT', tmp)
        monkeypatch.setenv("NEXORA_CLIENT", "client-a")
        
        token_dir = tmp / 'runtime' / 'control'
        token_dir.mkdir(parents=True, exist_ok=True)
        tokens = {"client-a": "token-a", "client-b": "token-b"}
        token_dir.joinpath("tokens.json").write_text(json.dumps(tokens))
        
        client = TestClient(edge_app)
        
        # Test valid request
        form_data = {
            "private": "false",
            "run_id": "test-run",
            "round_id": "1",
            "base_model_hash": "dummyhash",
            "feature_schema_hash": SCHEMA_HASH,
            "architecture_id": ARCHITECTURE_ID,
            "client_id": "client-a",
            "protocol_version": "nexora-fed-v1"
        }
        
        # Valid token, valid ID
        with (tmp / 'dummy').open('wb') as f: f.write(b"dummy")
        
        # We expect a validation error on base_model_hash or schema since it's dummy,
        # but NOT an identity error.
        resp = client.post(
            "/api/v1/train", 
            headers={"Authorization": "Bearer token-a"},
            data=form_data,
            files={"base_model": ("dummy", open(tmp / 'dummy', 'rb'), "application/octet-stream")}
        )
        assert resp.status_code == 500 or resp.status_code == 400
        assert "Invalid or missing service token" not in resp.text
        assert "Client ID mismatch with service environment" not in resp.text
        
        # Invalid token
        resp = client.post(
            "/api/v1/train", 
            headers={"Authorization": "Bearer token-b"},
            data=form_data,
            files={"base_model": ("dummy", open(tmp / 'dummy', 'rb'), "application/octet-stream")}
        )
        assert resp.status_code == 401
        assert "Invalid or missing service token" in resp.text
        
        # Mismatched client ID
        form_data["client_id"] = "client-b"
        resp = client.post(
            "/api/v1/train", 
            headers={"Authorization": "Bearer token-a"},
            data=form_data,
            files={"base_model": ("dummy", open(tmp / 'dummy', 'rb'), "application/octet-stream")}
        )
        assert resp.status_code == 400
        assert "Client ID mismatch with service environment" in resp.text
        
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_coordinator_rollback_lifecycle_state(monkeypatch):
    """Test that coordinator correctly manages lifecycle_state on activate and rollback."""
    tmp = Path(tempfile.mkdtemp())
    try:
        import nexora.federation.coordinator as coord
        monkeypatch.setattr(coord, 'ROOT', tmp)
        
        token_dir = tmp / 'runtime' / 'control'
        token_dir.mkdir(parents=True, exist_ok=True)
        token_dir.joinpath("tokens.json").write_text(json.dumps({"coordinator": "coord-token"}))
        headers = {"Authorization": "Bearer coord-token"}
        
        client = TestClient(coord_app)
        
        # Create Model A (Active)
        registry_dir = tmp / 'models' / 'registry'
        registry_dir.mkdir(parents=True, exist_ok=True)
        
        meta_a = {
            'run_id': 'run-a',
            'lifecycle_state': 'active',
            'model_hash': 'hash-a'
        }
        (registry_dir / 'active.json').write_text(json.dumps(meta_a))
        
        # Create Model A manifest
        run_a_dir = tmp / 'artifacts' / 'runs' / 'run-a'
        run_a_dir.mkdir(parents=True, exist_ok=True)
        (run_a_dir / 'manifest.json').write_text(json.dumps({'lifecycle_state': 'active'}))
        
        # Create Model B Candidate
        run_b_dir = tmp / 'artifacts' / 'runs' / 'run-b'
        run_b_dir.mkdir(parents=True, exist_ok=True)
        weights_b = run_b_dir / 'round-1.safetensors'
        weights_b.write_bytes(b"dummy")
        
        manifest_b = {
            'run_id': 'run-b',
            'lifecycle_state': 'candidate',
            'dataset': 'synthetic',
            'threshold': 0.5,
            'validation_score': 0.8,
            'architecture_id': ARCHITECTURE_ID,
            'feature_schema_hash': SCHEMA_HASH,
            'rounds': [{'round': 1, 'model_hash': hashlib.sha256(b"dummy").hexdigest(), 'status': 'completed'}]
        }
        (run_b_dir / 'manifest.json').write_text(json.dumps(manifest_b))
        
        # Activate B
        resp = client.post("/api/v1/models/run-b/activate", headers=headers)
        assert resp.status_code == 200
        
        # Check that A is retired in history
        history = json.loads((registry_dir / 'history.json').read_text())
        assert len(history) == 1
        assert history[0]['run_id'] == 'run-a'
        assert history[0]['lifecycle_state'] == 'retired'
        
        # Check that A is retired in manifest
        man_a = json.loads((run_a_dir / 'manifest.json').read_text())
        assert man_a['lifecycle_state'] == 'retired'
        
        # Check that B is active in active.json and manifest
        active = json.loads((registry_dir / 'active.json').read_text())
        assert active['run_id'] == 'run-b'
        assert active['lifecycle_state'] == 'active'
        man_b = json.loads((run_b_dir / 'manifest.json').read_text())
        assert man_b['lifecycle_state'] == 'active'
        
        # Rollback
        resp = client.post("/api/v1/models/rollback", headers=headers)
        assert resp.status_code == 200
        
        # Check that B is retired in history and manifest
        history = json.loads((registry_dir / 'history.json').read_text())
        assert len(history) == 1
        assert history[0]['run_id'] == 'run-b'
        assert history[0]['lifecycle_state'] == 'retired'
        man_b = json.loads((run_b_dir / 'manifest.json').read_text())
        assert man_b['lifecycle_state'] == 'retired'
        
        # Check that A is active again
        active = json.loads((registry_dir / 'active.json').read_text())
        assert active['run_id'] == 'run-a'
        assert active['lifecycle_state'] == 'active'
        man_a = json.loads((run_a_dir / 'manifest.json').read_text())
        assert man_a['lifecycle_state'] == 'active'
        
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
