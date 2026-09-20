"""Persistent loopback edge service. Replay pauses safely on process restart."""
import asyncio, json, os, secrets, time, uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
import numpy as np
import httpx
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from nexora.data.synthetic import generate_subject, SCENARIOS
from nexora.features.extract import extract
from nexora.ml.train import Predictor

ROOT=Path(__file__).resolve().parents[3]
CLIENT=os.environ.get('NEXORA_CLIENT','client-a')
RUNTIME=ROOT/'runtime'/CLIENT; RUNTIME.mkdir(parents=True,exist_ok=True)
engine=create_engine('sqlite:///'+str(RUNTIME/'state.sqlite'),connect_args={'check_same_thread':False})
with engine.begin() as c:
    c.execute(text('CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY)'))
    c.execute(text('INSERT OR IGNORE INTO schema_version VALUES(1)'))
    c.execute(text('CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, body TEXT NOT NULL)'))
    c.execute(text('CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id), sequence INTEGER NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL, UNIQUE(session_id,sequence))'))
    c.execute(text('CREATE INDEX IF NOT EXISTS event_session ON events(session_id,sequence)'))
    c.execute(text('CREATE TABLE IF NOT EXISTS interventions(id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id), body TEXT NOT NULL)'))
    c.execute(text('CREATE TABLE IF NOT EXISTS feedback(id TEXT PRIMARY KEY, body TEXT NOT NULL)'))

def rows(sql,params=None):
    with engine.connect() as c: return [dict(r._mapping) for r in c.execute(text(sql),params or {})]
def execute(sql,params):
    with engine.begin() as c: c.execute(text(sql),params)
def save(s): execute('INSERT INTO sessions VALUES(:id,:body) ON CONFLICT(id) DO UPDATE SET body=:body',{'id':s['id'],'body':json.dumps(s)})
def get(sid):
    r=rows('SELECT body FROM sessions WHERE id=:id',{'id':sid})
    if not r: raise HTTPException(404,'Session not found')
    return json.loads(r[0]['body'])
def event(s,kind,body):
    seq=rows('SELECT COALESCE(MAX(sequence),0)+1 AS n FROM events WHERE session_id=:id',{'id':s['id']})[0]['n']
    e={'schema_version':'1.0','event_id':str(uuid.uuid4()),'session_id':s['id'],'sequence':seq,'event_type':kind,'occurred_at':datetime.now(timezone.utc).isoformat(),'payload':body}
    execute('INSERT INTO events VALUES(:id,:sid,:seq,:kind,:body)',{'id':e['event_id'],'sid':s['id'],'seq':seq,'kind':kind,'body':json.dumps(e)})
    return e

predictor=None
def coordinator_request(method,path,**kwargs):
    base=os.environ.get('NEXORA_COORDINATOR_URL','http://127.0.0.1:8100')
    return httpx.request(method,f'{base}{path}',verify=os.environ.get('NEXORA_CA_FILE') or True,**kwargs)
async def replay():
    while True:
        for row in rows('SELECT body FROM sessions'):
            s=json.loads(row['body'])
            if s['status']!='running': continue
            samples,labels,posture=generate_subject(0,s['seed'],scenario=s['scenario'])
            for _ in range(s['speed']):
                i=s['index']
                if i>=len(samples): s['status']='stopped'; break
                values=samples[i]
                obs={'event_time_s':i/4,'source_type':'synthetic','source_label':'Synthetic','signals':{key:None if not np.isfinite(v) else float(v) for key,v in zip(['eda_us','skin_temperature_c','acc_x_g','acc_y_g','acc_z_g'],values)},'heart_rate_bpm':None,'posture_angle_deg':float(posture[i])}
                event(s,'observation',obs)
                if posture[i]>20:
                    if s['posture_since'] is None:s['posture_since']=i/4
                else:s['posture_since']=None
                if i%20==0:
                    decision={'result':'no_action','reason_codes':['no_sustained_context'],'source_type':'synthetic','event_time_s':i/4}
                    if s['posture_since'] is not None and i/4-s['posture_since']>=30:
                        active=any(json.loads(r['body'])['status'] in ['offered','accepted'] for r in rows('SELECT body FROM interventions WHERE session_id=:id',{'id':s['id']}))
                        if active or i/4-s['last_prompt']<s['cooldown']:
                            decision.update(result='suppressed',reason_codes=['active_prompt_or_cooldown'])
                        else:
                            prompt={'id':str(uuid.uuid4()),'session_id':s['id'],'type':'posture','status':'offered','text':'Take a moment to adjust your posture if comfortable.','source':'Synthetic','event_time_s':i/4}
                            execute('INSERT INTO interventions VALUES(:id,:sid,:body)',{'id':prompt['id'],'sid':s['id'],'body':json.dumps(prompt)})
                            s['last_prompt']=i/4; event(s,'intervention',prompt); decision.update(result='triggered',reason_codes=['posture_above_20_for_30s'])
                    if i>=119:
                        feat=extract(samples[i-119:i+1]); event(s,'window_ready',feat)
                        if feat['values'] is None:
                            event(s,'prediction',{'abstained':True,'reason':feat['reason']})
                        elif predictor:
                            started=time.perf_counter(); p=predictor.predict(feat['values'])[0]
                            pred={'prediction_id':str(uuid.uuid4()),'abstained':False,'probabilities':p.tolist(),'predicted_class':int(p.argmax()),'model_id':'neural','model_hash':predictor.metadata['model_hash'],'inference_ms':(time.perf_counter()-started)*1000,'features':feat['values'],'source':'Synthetic'}
                            event(s,'prediction',pred)
                    event(s,'decision',decision)
                s['index']+=1
            save(s)
        await asyncio.sleep(.25)

@asynccontextmanager
async def lifespan(app):
    global predictor
    try: predictor=Predictor()
    except FileNotFoundError: predictor=None
    for r in rows('SELECT body FROM sessions'):
        s=json.loads(r['body'])
        if s['status']=='running': s['status']='paused'; save(s)
    task=asyncio.create_task(replay())
    yield
    task.cancel()

app=FastAPI(title='NEXORA Edge Research API',lifespan=lifespan)
# Same-origin browser boundary; cross-origin control requests are rejected.
@app.middleware('http')
async def origin_guard(request:Request,call_next):
    origin=request.headers.get('origin')
    if origin and origin!=str(request.base_url).rstrip('/'):
        from fastapi.responses import JSONResponse
        return JSONResponse({'error':'origin_rejected'},status_code=403)
    return await call_next(request)
class SessionRequest(BaseModel):
    scenario:str='normal'
    speed:int=Field(default=5)
    seed:int=Field(default=42,ge=0,le=1000000)
class FeedbackRequest(BaseModel):
    feedback_id:uuid.UUID
    action:str
    helpfulness:int|None=Field(default=None,ge=1,le=5)
    note:str=Field(default='',max_length=500)
class ExperimentRequest(BaseModel):
    mode:str
    rounds:int=Field(default=1,ge=1,le=5)
@app.get('/api/v1/health')
def health():
    coordinator_url=os.environ.get('NEXORA_COORDINATOR_URL','http://127.0.0.1:8100')
    ca_file=os.environ.get('NEXORA_CA_FILE')
    try:
        response=httpx.get(f'{coordinator_url}/health',timeout=.25,verify=ca_file or True)
        coordinator='available' if response.status_code==200 else 'unavailable'
    except httpx.HTTPError: coordinator='unavailable'
    return {'client_id':CLIENT,'status':'available','model_ready':predictor is not None,'transport':'TLS verified' if ca_file else 'Local HTTP','source':'Synthetic','coordinator':coordinator,'local_inference_during_outage':predictor is not None}
@app.get('/api/v1/sources')
def sources():return {'scenarios':SCENARIOS,'recorded_dataset_status':'unavailable'}
@app.get('/api/v1/sessions')
def sessions():return [json.loads(r['body']) for r in rows('SELECT body FROM sessions ORDER BY rowid DESC LIMIT 100')]
@app.post('/api/v1/sessions')
def create(body:SessionRequest):
    if body.scenario not in SCENARIOS or body.speed not in [1,5,20]:raise HTTPException(422,'Invalid scenario or speed')
    s={'id':str(uuid.uuid4()),**body.model_dump(),'status':'paused','index':0,'created_at':datetime.now(timezone.utc).isoformat(),'posture_since':None,'last_prompt':-1000,'cooldown':120,'dismissals':[]};save(s);return s
@app.post('/api/v1/sessions/{sid}/{action}')
def control(sid:str,action:str):
    s=get(sid)
    if action not in ['start','pause','stop']:raise HTTPException(404,'Unknown action')
    if s['status']=='stopped':raise HTTPException(409,'Stopped sessions cannot resume')
    s['status']={'start':'running','pause':'paused','stop':'stopped'}[action];save(s);return s
@app.get('/api/v1/sessions/{sid}/events')
def events(sid:str,after:int=0,limit:int=500):
    get(sid)
    if after<0 or not 1<=limit<=1000:raise HTTPException(422,'Invalid pagination')
    return [json.loads(r['body']) for r in rows('SELECT body FROM events WHERE session_id=:id AND sequence>:after ORDER BY sequence LIMIT :limit',{'id':sid,'after':after,'limit':limit})]
@app.websocket('/api/v1/sessions/{sid}/stream')
async def stream(websocket:WebSocket,sid:str,after:int=0):
    origin=websocket.headers.get('origin'); host=websocket.headers.get('host')
    if origin and origin not in {f'http://{host}',f'https://{host}'}:
        await websocket.close(code=1008); return
    try: get(sid)
    except HTTPException:
        await websocket.close(code=1008); return
    cursor=max(0,after); await websocket.accept()
    try:
        while True:
            batch=rows('SELECT body FROM events WHERE session_id=:id AND sequence>:after ORDER BY sequence LIMIT 500',{'id':sid,'after':cursor})
            for row in batch:
                envelope=json.loads(row['body']); cursor=envelope['sequence']; await websocket.send_json(envelope)
            await asyncio.sleep(.2)
    except WebSocketDisconnect: pass
@app.get('/api/v1/interventions')
def interventions():return [json.loads(r['body']) for r in rows('SELECT body FROM interventions ORDER BY rowid DESC LIMIT 100')]
@app.post('/api/v1/interventions/{iid}/feedback')
def feedback(iid:str,body:FeedbackRequest):
    previous=rows('SELECT body FROM feedback WHERE id=:id',{'id':str(body.feedback_id)})
    if previous:return json.loads(previous[0]['body'])
    r=rows('SELECT body FROM interventions WHERE id=:id',{'id':iid})
    if not r:raise HTTPException(404,'Unknown intervention')
    item=json.loads(r[0]['body']); allowed={'offered':{'accept':'accepted','dismiss':'dismissed'},'accepted':{'complete':'completed','cancel':'cancelled'}}
    if body.action not in allowed.get(item['status'],{}):raise HTTPException(409,'Invalid intervention transition')
    item['status']=allowed[item['status']][body.action]
    execute('UPDATE interventions SET body=:body WHERE id=:id',{'id':iid,'body':json.dumps(item)})
    s=get(item['session_id']); record={**body.model_dump(mode='json'),'intervention_id':iid,'source':'Manual feedback','created_at':datetime.now(timezone.utc).isoformat()}
    execute('INSERT INTO feedback VALUES(:id,:body)',{'id':str(body.feedback_id),'body':json.dumps(record)})
    event(s,'feedback',record)
    if body.action=='dismiss':
        s['dismissals']=[t for t in s['dismissals'] if s['index']/4-t<=600]+[s['index']/4]
        if len(s['dismissals'])>=2:
            s['cooldown']=min(600,s['cooldown']*2); s['dismissals']=[];event(s,'policy_changed',{'cooldown_s':s['cooldown'],'reason':'two_dismissals_within_10min'})
        save(s)
    return item
@app.get('/api/v1/metrics')
def metrics():return [json.loads(p.read_text()) for p in (ROOT/'models').glob('*/metadata.json')]
@app.get('/api/v1/experiments')
def experiments():
    manifests=[]
    for path in (ROOT/'artifacts/runs').glob('*/manifest.json'):
        try: manifests.append(json.loads(path.read_text()))
        except (OSError,json.JSONDecodeError): continue
    return sorted(manifests,key=lambda item:item['run_id'],reverse=True)
@app.get('/api/v1/experiment-jobs')
def experiment_jobs():
    try: response=coordinator_request('GET','/api/v1/jobs',timeout=1)
    except httpx.HTTPError: raise HTTPException(503,'Coordinator unavailable')
    if response.status_code!=200: raise HTTPException(response.status_code,response.text)
    return response.json()
@app.post('/api/v1/experiment-jobs',status_code=202)
def create_experiment_job(body:ExperimentRequest):
    try: response=coordinator_request('POST','/api/v1/experiments',json=body.model_dump(),timeout=2)
    except httpx.HTTPError: raise HTTPException(503,'Coordinator unavailable')
    if response.status_code!=202: raise HTTPException(response.status_code,response.text)
    return response.json()
@app.get('/api/v1/experiment-jobs/{job_id}')
def experiment_job(job_id:str):
    try: response=coordinator_request('GET',f'/api/v1/experiments/{job_id}',timeout=1)
    except httpx.HTTPError: raise HTTPException(503,'Coordinator unavailable')
    if response.status_code!=200: raise HTTPException(response.status_code,response.text)
    return response.json()
@app.post('/api/v1/experiment-jobs/{job_id}/cancel')
def cancel_experiment_job(job_id:str):
    try: response=coordinator_request('POST',f'/api/v1/experiments/{job_id}/cancel',timeout=2)
    except httpx.HTTPError: raise HTTPException(503,'Coordinator unavailable')
    if response.status_code!=200: raise HTTPException(response.status_code,response.text)
    return response.json()
@app.get('/api/v1/privacy')
def privacy():
    ledgers=[]
    for path in (ROOT/'runtime').glob('client-*/privacy.json'):
        try: ledgers.append(json.loads(path.read_text()))
        except (OSError,json.JSONDecodeError): continue
    return sorted(ledgers,key=lambda item:item['client_id'])
@app.get('/api/v1/explanations/{pid}')
def explain(pid:str,model:str='neural'):
    if model not in ['neural','baseline']: raise HTTPException(422,'Unknown model')
    for r in rows("SELECT body FROM events WHERE kind='prediction' ORDER BY rowid DESC LIMIT 500"):
        p=json.loads(r['body'])['payload']
        if p.get('prediction_id')==pid:return (predictor if model=='neural' else Predictor('baseline')).explain(p['features'])
    raise HTTPException(404,'Prediction not found')
if (ROOT/'frontend/dist').exists():
    app.mount('/',StaticFiles(directory=ROOT/'frontend/dist',html=True),name='dashboard')
