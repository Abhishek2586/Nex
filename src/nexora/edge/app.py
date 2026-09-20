"""Persistent loopback edge service. Replay pauses safely on process restart."""
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from nexora.edge.store import rows, save
from nexora.edge.inference import init_predictor
from nexora.edge.replay import replay_task

from nexora.edge.routes import health, sessions, events, interventions, explanations, federation

ROOT = Path(__file__).resolve().parents[3]

@asynccontextmanager
async def lifespan(app):
    import json
    init_predictor()
    for r in rows('SELECT body FROM sessions'):
        s = json.loads(r['body'])
        if s['status'] == 'running':
            s['status'] = 'paused'
            save(s)
    task = asyncio.create_task(replay_task())
    yield
    task.cancel()

app = FastAPI(title='NEXORA Edge Research API', lifespan=lifespan)

@app.middleware('http')
async def origin_guard(request: Request, call_next):
    origin = request.headers.get('origin')
    if origin and origin not in (str(request.base_url).rstrip('/'), 'http://localhost:5173', 'http://127.0.0.1:5173'):
        from fastapi.responses import JSONResponse
        return JSONResponse({'error': 'origin_rejected'}, status_code=403)
    return await call_next(request)

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

app.include_router(health.router, prefix='/api/v1')
app.include_router(sessions.router, prefix='/api/v1')
app.include_router(events.router, prefix='/api/v1')
app.include_router(interventions.router, prefix='/api/v1')
app.include_router(explanations.router, prefix='/api/v1')
app.include_router(federation.router, prefix='/api/v1')

if (ROOT / 'frontend/dist').exists():
    app.mount('/', StaticFiles(directory=ROOT / 'frontend/dist', html=True), name='dashboard')

