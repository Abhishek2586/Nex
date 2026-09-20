import asyncio
import json
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from nexora.edge.store import rows, get

router = APIRouter()

@router.get('/sessions/{sid}/events')
def events(sid: str, after: int = 0, limit: int = 500):
    get(sid)
    if after < 0 or not 1 <= limit <= 1000:
        raise HTTPException(422, 'Invalid pagination')
    return [json.loads(r['body']) for r in rows('SELECT body FROM events WHERE session_id=:id AND sequence>:after ORDER BY sequence LIMIT :limit', {'id': sid, 'after': after, 'limit': limit})]

@router.websocket('/sessions/{sid}/stream')
async def stream(websocket: WebSocket, sid: str, after: int = 0):
    origin = websocket.headers.get('origin')
    host = websocket.headers.get('host')
    if origin and origin not in {f'http://{host}', f'https://{host}', 'http://localhost:5173', 'http://127.0.0.1:5173'}:
        await websocket.close(code=1008)
        return
    try: 
        get(sid)
    except HTTPException:
        await websocket.close(code=1008)
        return
    
    cursor = max(0, after)
    await websocket.accept()
    try:
        while True:
            batch = rows('SELECT body FROM events WHERE session_id=:id AND sequence>:after ORDER BY sequence LIMIT 500', {'id': sid, 'after': cursor})
            for row in batch:
                envelope = json.loads(row['body'])
                cursor = envelope['sequence']
                await websocket.send_json(envelope)
            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        pass
