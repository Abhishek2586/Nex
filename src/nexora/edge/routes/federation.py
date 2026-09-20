import os
import json
import httpx
from fastapi import APIRouter, HTTPException
from pathlib import Path
from nexora.edge.schemas import ExperimentRequest

router = APIRouter()
ROOT = Path(__file__).resolve().parents[4]

def coordinator_request(method, path, **kwargs):
    base = os.environ.get('NEXORA_COORDINATOR_URL', 'http://127.0.0.1:8100')
    ca_file = os.environ.get('NEXORA_CA_FILE')
    return httpx.request(method, f'{base}{path}', verify=ca_file or True, **kwargs)

@router.get('/metrics')
def metrics():
    return [json.loads(p.read_text()) for p in (ROOT / 'models').glob('*/metadata.json')]

@router.get('/experiments')
def experiments():
    manifests = []
    for path in (ROOT / 'artifacts/runs').glob('*/manifest.json'):
        try:
            manifests.append(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError):
            continue
    return sorted(manifests, key=lambda item: item['run_id'], reverse=True)

@router.get('/experiment-jobs')
def experiment_jobs():
    try: 
        response = coordinator_request('GET', '/api/v1/jobs', timeout=1)
    except httpx.HTTPError: 
        raise HTTPException(503, 'Coordinator unavailable')
    if response.status_code != 200: 
        raise HTTPException(response.status_code, response.text)
    return response.json()

@router.post('/experiment-jobs', status_code=202)
def create_experiment_job(body: ExperimentRequest):
    try: 
        response = coordinator_request('POST', '/api/v1/experiments', json=body.model_dump(), timeout=2)
    except httpx.HTTPError: 
        raise HTTPException(503, 'Coordinator unavailable')
    if response.status_code != 202: 
        raise HTTPException(response.status_code, response.text)
    return response.json()

@router.get('/experiment-jobs/{job_id}')
def experiment_job(job_id: str):
    try: 
        response = coordinator_request('GET', f'/api/v1/experiments/{job_id}', timeout=1)
    except httpx.HTTPError: 
        raise HTTPException(503, 'Coordinator unavailable')
    if response.status_code != 200: 
        raise HTTPException(response.status_code, response.text)
    return response.json()

@router.post('/experiment-jobs/{job_id}/cancel')
def cancel_experiment_job(job_id: str):
    try: 
        response = coordinator_request('POST', f'/api/v1/experiments/{job_id}/cancel', timeout=2)
    except httpx.HTTPError: 
        raise HTTPException(503, 'Coordinator unavailable')
    if response.status_code != 200: 
        raise HTTPException(response.status_code, response.text)
    return response.json()

@router.get('/privacy')
def privacy():
    ledgers = []
    for path in (ROOT / 'runtime').glob('client-*/privacy.json'):
        try:
            ledgers.append(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError):
            continue
    return sorted(ledgers, key=lambda item: item.get('client_id', 'unknown'))

from fastapi import File, UploadFile, Form
import tempfile
import uuid
import shutil
from nexora.federation.client_worker import train_client

@router.post('/train')
async def train(
    base_model: UploadFile = File(...),
    private: bool = Form(False),
    client_id: str = Form(None)
):
    cid = client_id or os.environ.get('NEXORA_CLIENT', 'client-a')
    run_id = str(uuid.uuid4())
    work_dir = ROOT / 'runtime' / cid / 'federation' / run_id
    work_dir.mkdir(parents=True, exist_ok=True)
    
    base_path = work_dir / 'base.safetensors'
    output_path = work_dir / 'output.safetensors'
    
    with base_path.open('wb') as f:
        shutil.copyfileobj(base_model.file, f)
        
    try:
        metadata = train_client(cid, base_path, output_path, private)
    except Exception as e:
        raise HTTPException(500, f'Training failed: {str(e)}')
        
    if not output_path.exists():
        raise HTTPException(500, 'Output model missing')
        
    # Return the metadata and the trained model file
    from fastapi.responses import FileResponse
    response = FileResponse(path=output_path, media_type='application/octet-stream')
    response.headers['X-Federation-Metadata'] = json.dumps(metadata)
    return response
