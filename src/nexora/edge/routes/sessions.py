import uuid
import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from nexora.edge.schemas import SessionRequest
from nexora.edge.store import rows, save, get
from nexora.data.synthetic import SCENARIOS

router = APIRouter()

@router.get('/sources')
def sources():
    return {'scenarios': SCENARIOS, 'recorded_dataset_status': 'unavailable'}

@router.get('/sessions')
def sessions():
    return [json.loads(r['body']) for r in rows('SELECT body FROM sessions ORDER BY rowid DESC LIMIT 100')]

@router.post('/sessions')
def create(body: SessionRequest):
    if body.scenario not in SCENARIOS or body.speed not in [1, 5, 20]:
        raise HTTPException(422, 'Invalid scenario or speed')
    s = {
        'id': str(uuid.uuid4()),
        **body.model_dump(),
        'status': 'paused',
        'index': 0,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'posture_since': None,
        'last_prompt': -1000,
        'last_prompt_breathing': -1000,
        'cooldown': 120,
        'cooldown_posture': 120,
        'cooldown_breathing': 240,
        'dismissals_posture': [],
        'dismissals_breathing': []
    }
    save(s)
    return s

@router.post('/sessions/{sid}/{action}')
def control(sid: str, action: str):
    s = get(sid)
    if action not in ['start', 'pause', 'stop']:
        raise HTTPException(404, 'Unknown action')
    transitions = {
        'start': {'paused': 'running'},
        'pause': {'running': 'paused'},
        'stop': {'paused': 'stopped', 'running': 'stopped'},
    }
    next_status = transitions[action].get(s['status'])
    if next_status is None:
        raise HTTPException(409, f"Cannot {action} a session that is {s['status']}")
    s['status'] = next_status
    save(s)
    return s
