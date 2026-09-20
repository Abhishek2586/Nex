"""Loopback coordinator status and persisted public experiment metadata."""
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[3]
app = FastAPI(title="NEXORA Local Federation Coordinator")
JOBS=ROOT/'runtime/coordinator/jobs'; JOBS.mkdir(parents=True,exist_ok=True)
processes={}; lock=threading.Lock()

class ExperimentRequest(BaseModel):
    mode:str
    rounds:int=Field(default=1,ge=1,le=5)

def _save(job):
    (JOBS/f"{job['job_id']}.json").write_text(json.dumps(job,indent=2))

def _load(job_id):
    path=JOBS/f'{job_id}.json'
    if not path.exists(): raise HTTPException(404,'Experiment job not found')
    return json.loads(path.read_text())

def _execute(job):
    job.update(status='training',started_at=time.time()); _save(job)
    command=[sys.executable,'-m','nexora.cli','experiment','run','--mode',job['mode'],'--dataset','synthetic','--rounds',str(job['rounds'])]
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

@app.get("/api/v1/experiments")
def experiments():
    results = []
    for path in (ROOT / "artifacts" / "runs").glob("*/manifest.json"):
        try: results.append(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError): continue
    return sorted(results, key=lambda item: item["run_id"], reverse=True)

@app.get('/api/v1/jobs')
def jobs():
    return sorted([json.loads(path.read_text()) for path in JOBS.glob('*.json')],key=lambda item:item['created_at'],reverse=True)

@app.post('/api/v1/experiments',status_code=202)
def create_experiment(body:ExperimentRequest):
    if body.mode not in ['federated','private-federated']: raise HTTPException(422,'Unsupported mode')
    if any(item['status'] in ['queued','training'] for item in jobs()): raise HTTPException(409,'Another experiment is active')
    job={'job_id':str(uuid.uuid4()),'mode':body.mode,'rounds':body.rounds,'source':'Synthetic','status':'queued','created_at':time.time()}
    _save(job); threading.Thread(target=_execute,args=(job,),daemon=True).start(); return job

@app.get('/api/v1/experiments/{job_id}')
def experiment(job_id:str): return _load(job_id)

@app.post('/api/v1/experiments/{job_id}/cancel')
def cancel(job_id:str):
    job=_load(job_id)
    if job['status'] not in ['queued','training']: raise HTTPException(409,'Experiment is not active')
    with lock: process=processes.get(job_id)
    if process and process.poll() is None: process.terminate()
    job.update(status='cancelled',finished_at=time.time()); _save(job); return job
