import pytest
from fastapi.testclient import TestClient
from nexora.edge.app import app

def test_invalid_session_creation():
    with TestClient(app) as c:
        # Invalid scenario
        res = c.post('/api/v1/sessions', json={'scenario': 'non_existent_scenario', 'speed': 1})
        assert res.status_code == 422
        
        # Invalid speed
        res = c.post('/api/v1/sessions', json={'scenario': 'normal', 'speed': 1000})
        assert res.status_code == 422
        
        # Missing payload
        res = c.post('/api/v1/sessions', json={})
        assert res.status_code == 422

def test_invalid_state_transitions():
    with TestClient(app) as c:
        session = c.post('/api/v1/sessions', json={'scenario': 'normal', 'speed': 1}).json()
        sid = session['id']
        
        # Start session
        res = c.post(f"/api/v1/sessions/{sid}/start", json={})
        assert res.status_code == 200
        
        # Start again should conflict
        res = c.post(f"/api/v1/sessions/{sid}/start", json={})
        assert res.status_code == 409
        
        # Pause
        res = c.post(f"/api/v1/sessions/{sid}/pause", json={})
        assert res.status_code == 200
        
        # Stop
        res = c.post(f"/api/v1/sessions/{sid}/stop", json={})
        assert res.status_code == 200
        
        # Start after stopped should fail
        res = c.post(f"/api/v1/sessions/{sid}/start", json={})
        assert res.status_code == 409

def test_missing_auth_on_training():
    with TestClient(app) as c:
        # We need a dummy file for the upload
        import io
        files = {'base_model': ('dummy.safetensors', io.BytesIO(b'dummy content'), 'application/octet-stream')}
        # Missing auth header should fail with 401
        res = c.post('/api/v1/train', files=files, data={'private': False})
        assert res.status_code == 401

def test_invalid_job_id():
    with TestClient(app) as c:
        res = c.get('/api/v1/experiment-jobs/invalid_id')
        # Since coordinator is likely unavailable in this simple test environment, it might return 503
        assert res.status_code in [404, 503]

def test_schema_validation_events():
    with TestClient(app) as c:
        # Non-existent session events
        res = c.get('/api/v1/sessions/non_existent_session/events')
        assert res.status_code == 404
