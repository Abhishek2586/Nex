import json, os, uuid
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[3]
CLIENT = os.environ.get('NEXORA_CLIENT', 'client-a')
RUNTIME = ROOT / 'runtime' / CLIENT
RUNTIME.mkdir(parents=True, exist_ok=True)
engine = create_engine('sqlite:///' + str(RUNTIME / 'state.sqlite'), connect_args={'check_same_thread': False})

with engine.begin() as c:
    c.execute(text('CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY)'))
    c.execute(text('INSERT OR IGNORE INTO schema_version VALUES(1)'))
    c.execute(text('CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, body TEXT NOT NULL)'))
    c.execute(text('CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id), sequence INTEGER NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL, UNIQUE(session_id,sequence))'))
    c.execute(text('CREATE INDEX IF NOT EXISTS event_session ON events(session_id,sequence)'))
    c.execute(text('CREATE TABLE IF NOT EXISTS interventions(id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id), body TEXT NOT NULL)'))
    c.execute(text('CREATE TABLE IF NOT EXISTS feedback(id TEXT PRIMARY KEY, body TEXT NOT NULL)'))

def rows(sql, params=None):
    with engine.connect() as c:
        return [dict(r._mapping) for r in c.execute(text(sql), params or {})]

def execute(sql, params):
    with engine.begin() as c:
        c.execute(text(sql), params)

def save(s):
    execute('INSERT INTO sessions VALUES(:id,:body) ON CONFLICT(id) DO UPDATE SET body=:body', {'id': s['id'], 'body': json.dumps(s)})

def get(sid):
    r = rows('SELECT body FROM sessions WHERE id=:id', {'id': sid})
    if not r: raise HTTPException(404, 'Session not found')
    return json.loads(r[0]['body'])

from nexora.edge.schemas import Observation, Prediction, Decision

def event(s, kind, body):
    if kind == 'observation':
        Observation(**body)
    elif kind == 'prediction':
        Prediction(**body)
    elif kind == 'decision':
        Decision(**body)
        
    # Concurrency safe sequence generator with retry
    import sqlalchemy.exc
    for attempt in range(5):
        try:
            seq_val = rows('SELECT COALESCE(MAX(sequence),0)+1 AS n FROM events WHERE session_id=:id', {'id': s['id']})[0]['n']
            e = {
                'schema_version': '1.0', 
                'event_id': str(uuid.uuid4()), 
                'session_id': s['id'], 
                'sequence': seq_val, 
                'event_type': kind, 
                'occurred_at': datetime.now(timezone.utc).isoformat(), 
                'payload': body
            }
            execute('INSERT INTO events VALUES(:id,:sid,:seq,:kind,:body)', 
                    {'id': e['event_id'], 'sid': s['id'], 'seq': seq_val, 'kind': kind, 'body': json.dumps(e)})
            return e
        except sqlalchemy.exc.IntegrityError:
            if attempt == 4: raise
            import time
            time.sleep(0.01 * (attempt + 1))
