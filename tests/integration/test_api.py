import uuid
import pytest
from fastapi.testclient import TestClient
from nexora.edge.app import app
from nexora.edge.store import event, get

def test_session_and_origin_boundary():
    with TestClient(app) as c:
        health=c.get('/api/v1/health').json()
        assert health['model_ready'] in [True, False]
        assert health['local_inference_during_outage'] in [True, False]
        assert health['coordinator'] in ['available','unavailable']
        assert c.post('/api/v1/sessions',json={'scenario':'bad'}).status_code==422
        assert c.post('/api/v1/sessions',json={},headers={'origin':'https://untrusted.example'}).status_code==403
        s=c.post('/api/v1/sessions',json={'scenario':'brief_posture','speed':20}).json()
        assert c.post(f"/api/v1/sessions/{s['id']}/start",json={}).json()['status']=='running'
        assert c.post(f"/api/v1/sessions/{s['id']}/pause",json={}).json()['status']=='paused'
        assert c.post(f"/api/v1/sessions/{s['id']}/stop",json={}).json()['status']=='stopped'
        assert c.post(f"/api/v1/sessions/{s['id']}/start",json={}).status_code==409

def test_websocket_catchup_and_origin_rejection():
    with TestClient(app) as c:
        session=c.post('/api/v1/sessions',json={'scenario':'normal','speed':1}).json()
        created=event(get(session['id']),'connection_status',{'state':'test'})
        with c.websocket_connect(f"/api/v1/sessions/{session['id']}/stream?after=0") as socket:
            received=socket.receive_json()
            assert received['event_id']==created['event_id']
            assert received['sequence']==1
        with pytest.raises(Exception):
            with c.websocket_connect(f"/api/v1/sessions/{session['id']}/stream",headers={'origin':'https://untrusted.example'}):
                pass
