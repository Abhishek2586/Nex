import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from nexora.edge.schemas import FeedbackRequest
from nexora.edge.store import rows, execute, get, event, save

router = APIRouter()

@router.get('/interventions')
def interventions():
    return [json.loads(r['body']) for r in rows('SELECT body FROM interventions ORDER BY rowid DESC LIMIT 100')]

@router.post('/interventions/{iid}/feedback')
def feedback(iid: str, body: FeedbackRequest):
    previous = rows('SELECT body FROM feedback WHERE id=:id', {'id': str(body.feedback_id)})
    if previous:
        return json.loads(previous[0]['body'])
    
    r = rows('SELECT body FROM interventions WHERE id=:id', {'id': iid})
    if not r:
        raise HTTPException(404, 'Unknown intervention')
    
    item = json.loads(r[0]['body'])
    allowed = {'offered': {'accept': 'accepted', 'dismiss': 'dismissed'}, 'accepted': {'complete': 'completed', 'cancel': 'cancelled'}}
    if body.action not in allowed.get(item['status'], {}):
        raise HTTPException(409, 'Invalid intervention transition')
    
    item['status'] = allowed[item['status']][body.action]
    execute('UPDATE interventions SET body=:body WHERE id=:id', {'id': iid, 'body': json.dumps(item)})
    
    s = get(item['session_id'])
    record = {**body.model_dump(mode='json'), 'intervention_id': iid, 'source': 'Manual feedback', 'created_at': datetime.now(timezone.utc).isoformat()}
    execute('INSERT INTO feedback VALUES(:id,:body)', {'id': str(body.feedback_id), 'body': json.dumps(record)})
    event(s, 'feedback', record)
    
    if body.action == 'dismiss':
        itype = item.get('type', 'posture')
        dismissals_key = f'dismissals_{itype}'
        cooldown_key = f'cooldown_{itype}'
        
        current_time_s = s.get('index', 0) / 4.0
        
        if dismissals_key not in s: s[dismissals_key] = []
        if cooldown_key not in s: s[cooldown_key] = 120
        
        # Keep dismissals within last 10 minutes (600s)
        s[dismissals_key] = [t for t in s[dismissals_key] if current_time_s - t <= 600] + [current_time_s]
        
        if len(s[dismissals_key]) >= 2:
            s[cooldown_key] = min(1200, s[cooldown_key] * 2)
            s[dismissals_key] = []
            event(s, 'policy_changed', {'cooldown_s': s[cooldown_key], 'type': itype, 'reason': f'two_{itype}_dismissals_within_10min'})
        save(s)
        
    return item
