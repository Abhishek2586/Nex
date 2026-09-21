"""Loopback coordinator status and persisted public experiment metadata."""
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
import hashlib
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]
app = FastAPI(title="NEXORA Local Federation Coordinator")

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, 'Missing or invalid token format')
    token = authorization.split(' ')[1]
    
    token_path = ROOT / 'runtime/control/tokens.json'
    if not token_path.exists():
        raise HTTPException(401, 'Tokens not initialized')
        
    tokens = json.loads(token_path.read_text())
    # Coordinator accepts its own token, or any client's token
    if token not in tokens.values():
        raise HTTPException(401, 'Invalid service token')
JOBS=ROOT/'runtime/coordinator/jobs'; JOBS.mkdir(parents=True,exist_ok=True)
processes={}; lock=threading.Lock()

class ExperimentRequest(BaseModel):
    mode:str
    rounds:int=Field(default=1,ge=1,le=5)
    dataset:str=Field(default='synthetic')

def _save(job):
    (JOBS/f"{job['job_id']}.json").write_text(json.dumps(job,indent=2))

def _load(job_id):
    path=JOBS/f'{job_id}.json'
    if not path.exists(): raise HTTPException(404,'Experiment job not found')
    return json.loads(path.read_text())

def _execute(job):
    job.update(status='training',started_at=time.time()); _save(job)
    command=[sys.executable,'-m','nexora.cli','experiment','run','--mode',job['mode'],'--dataset',job['dataset'],'--rounds',str(job['rounds'])]
    process=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    with lock: processes[job['job_id']]=process
    stdout,stderr=process.communicate()
    with lock: processes.pop(job['job_id'],None)
    current=_load(job['job_id'])
    if current['status']=='cancelled': return
    if process.returncode:
        current.update(status='failed',finished_at=time.time(),error=stderr[-2000:]); _save(current); return
    try: result=json.loads(stdout)
    except json.JSONDecodeError:
        current.update(status='failed',finished_at=time.time(),error='Experiment returned invalid output'); _save(current); return
    current.update(status='completed',finished_at=time.time(),run_id=result['run_id'],result=result); _save(current)

@app.get("/health")
def health():
    manifests = list((ROOT / "artifacts" / "runs").glob("*/manifest.json"))
    return {"status": "available", "role": "coordinator", "completed_runs": len(manifests), "transport": "Local HTTP"}

@app.get("/api/v1/experiments", dependencies=[Depends(verify_token)])
def experiments():
    results = []
    for path in (ROOT / "artifacts" / "runs").glob("*/manifest.json"):
        try: results.append(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError): continue
    return sorted(results, key=lambda item: item["run_id"], reverse=True)

@app.get('/api/v1/jobs', dependencies=[Depends(verify_token)])
def jobs():
    return sorted([json.loads(path.read_text()) for path in JOBS.glob('*.json')],key=lambda item:item['created_at'],reverse=True)

@app.post('/api/v1/experiments',status_code=202, dependencies=[Depends(verify_token)])
def create_experiment(body:ExperimentRequest):
    if body.mode not in ['federated','private-federated']: raise HTTPException(422,'Unsupported mode')
    if any(item['status'] in ['queued','training'] for item in jobs()): raise HTTPException(409,'Another experiment is active')
    job={'job_id':str(uuid.uuid4()),'mode':body.mode,'rounds':body.rounds,'source':'Synthetic','status':'queued','created_at':time.time()}
    _save(job); threading.Thread(target=_execute,args=(job,),daemon=True).start(); return job

@app.get('/api/v1/experiments/{job_id}', dependencies=[Depends(verify_token)])
def experiment(job_id:str): return _load(job_id)

@app.post('/api/v1/experiments/{job_id}/cancel', dependencies=[Depends(verify_token)])
def cancel(job_id:str):
    job=_load(job_id)
    if job['status'] not in ['queued','training']: raise HTTPException(409,'Experiment is not active')
    with lock: process=processes.get(job_id)
    if process and process.poll() is None: process.terminate()
    job.update(status='cancelled',finished_at=time.time()); _save(job); return job

@app.post('/api/v1/models/{run_id}/activate', dependencies=[Depends(verify_token)])
def activate_model(run_id: str, body: dict = None):
    # 'body' might optionally contain 'round'. If not, default to the last round.
    round_number = body.get('round', 1) if body else 1
    run_path = ROOT / 'artifacts' / 'runs' / run_id
    if not run_path.exists(): raise HTTPException(404, 'Run not found')
    manifest = json.loads((run_path / 'manifest.json').read_text())
    
    # Validation checks
    if len(manifest['rounds']) < round_number: raise HTTPException(422, 'Round not found in run')
    round_meta = manifest['rounds'][round_number - 1]
    
    safetensor_path = run_path / f"round-{round_number}.safetensors"
    if not safetensor_path.exists(): raise HTTPException(404, 'Model weights missing')
    
    b_hash = hashlib.sha256(safetensor_path.read_bytes()).hexdigest()
    if b_hash != round_meta['model_hash']: raise HTTPException(400, 'Model hash mismatch validation failed')
    
    registry_dir = ROOT / 'models' / 'registry'
    registry_dir.mkdir(parents=True, exist_ok=True)
    
    meta = {
        'source': manifest.get('dataset', 'synthetic'),
        'model_id': 'neural',
        'run_id': run_id,
        'round': round_number,
        'model_hash': round_meta['model_hash'],
        'feature_schema_hash': manifest.get('feature_schema_hash', ''),
        'artifact_path': str(safetensor_path),
        'metrics': round_meta.get('metrics', {}),
        'activated_at': time.time()
    }
    
    # Save history if active exists
    active_path = registry_dir / 'active.json'
    if active_path.exists():
        history_path = registry_dir / 'history.json'
        history = json.loads(history_path.read_text()) if history_path.exists() else []
        history.append(json.loads(active_path.read_text()))
        history_path.write_text(json.dumps(history, indent=2))
        
    active_path.write_text(json.dumps(meta, indent=2))
    return meta

@app.post('/api/v1/models/rollback', dependencies=[Depends(verify_token)])
def rollback_model():
    registry_dir = ROOT / 'models' / 'registry'
    active_path = registry_dir / 'active.json'
    history_path = registry_dir / 'history.json'
    
    if not active_path.exists() or not history_path.exists():
        raise HTTPException(400, 'No history to rollback to')
        
    history = json.loads(history_path.read_text())
    if not history:
        raise HTTPException(400, 'History is empty')
        
    previous = history.pop()
    active_path.write_text(json.dumps(previous, indent=2))
    history_path.write_text(json.dumps(history, indent=2))
    return previous

@app.get('/api/v1/models/active')
def get_active_model():
    target_meta = ROOT / 'models' / 'registry' / 'active.json'
    if not target_meta.exists(): raise HTTPException(404, 'No active model')
    return json.loads(target_meta.read_text())

