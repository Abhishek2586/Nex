import os
import json
import httpx
from fastapi import APIRouter, HTTPException
from pathlib import Path
from nexora.edge.schemas import ExperimentRequest

router = APIRouter()
ROOT = Path(__file__).resolve().parents[4]
_projection_cache = []
_projection_cache_key = None

def coordinator_request(method, path, **kwargs):
    base = os.environ.get('NEXORA_COORDINATOR_URL', 'http://127.0.0.1:8100')
    ca_file = os.environ.get('NEXORA_CA_FILE')
    expected_token = (ROOT / 'runtime/control/tokens.json').read_text() if (ROOT / 'runtime/control/tokens.json').exists() else '{}'
    tokens = json.loads(expected_token)
    cid = os.environ.get('NEXORA_CLIENT', 'client-a')
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f"Bearer {tokens.get(cid, '')}"
    return httpx.request(method, f'{base}{path}', verify=ca_file or True, headers=headers, **kwargs)

@router.get('/metrics')
def metrics():
    active_path = ROOT / 'models/registry/active.json'
    history_path = ROOT / 'models/registry/history.json'
    results = []
    
    if history_path.exists():
        try: results.extend(json.loads(history_path.read_text()))
        except Exception: pass
        
    if active_path.exists():
        try: results.append(json.loads(active_path.read_text()))
        except Exception: pass
        
    return results

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

@router.get('/privacy/projection')
def privacy_projection():
    global _projection_cache, _projection_cache_key
    try:
        from opacus.accountants import RDPAccountant
    except ImportError:
        return []

    paths = sorted((ROOT / 'runtime').glob('client-*/privacy.json'))
    cache_key = tuple((str(path), path.stat().st_mtime_ns) for path in paths)
    if cache_key == _projection_cache_key:
        return _projection_cache

    ledgers = []
    for path in paths:
        try:
            ledger = json.loads(path.read_text())
            delta = ledger.get("delta", 1e-5)
            
            projected = RDPAccountant()
            projected.history = [tuple(item) for item in ledger.get("history", [])]
            
            if not projected.history:
                continue
                
            last_noise, last_sample_rate, last_steps = projected.history[-1]
            
            # Next round epsilon
            proj_next = RDPAccountant()
            proj_next.history = [tuple(item) for item in ledger.get("history", [])]
            proj_next.history.append((last_noise, last_sample_rate, last_steps))
            next_eps = proj_next.get_epsilon(delta)
            
            # Calculate remaining rounds
            test_proj = RDPAccountant()
            test_proj.history = [tuple(item) for item in ledger.get("history", [])]
            remaining = 0
            # The UI needs a small planning hint, not an expensive unbounded
            # accountant simulation on every two-second dashboard refresh.
            while test_proj.get_epsilon(delta) <= 8.0 and remaining < 20:
                test_proj.history.append((last_noise, last_sample_rate, last_steps))
                remaining += 1
                
            ledgers.append({
                "client_id": ledger.get("client_id", "unknown"),
                "current_epsilon": ledger.get("epsilon", 0.0),
                "next_epsilon": float(next_eps),
                "remaining_rounds": max(0, remaining - 1),
                "max_epsilon": 8.0
            })
        except Exception:
            pass
    _projection_cache = sorted(ledgers, key=lambda item: item["client_id"])
    _projection_cache_key = cache_key
    return _projection_cache

from fastapi.responses import JSONResponse

@router.get('/evidence/export')
def export_evidence():
    active_path = ROOT / 'models/registry/active.json'
    history_path = ROOT / 'models/registry/history.json'
    
    evidence = {
        "metrics": [],
        "privacy": []
    }
    
    if history_path.exists():
        try: evidence["metrics"].extend(json.loads(history_path.read_text()))
        except Exception: pass
        
    if active_path.exists():
        try: evidence["metrics"].append(json.loads(active_path.read_text()))
        except Exception: pass
        
    for path in (ROOT / 'runtime').glob('client-*/privacy.json'):
        try: evidence["privacy"].append(json.loads(path.read_text()))
        except Exception: pass
        
    return JSONResponse(content=evidence, headers={"Content-Disposition": "attachment; filename=evidence.json"})

from fastapi import File, UploadFile, Form, Header
import uuid
import shutil
from nexora.federation.client_worker import train_client

@router.post('/train')
async def train(
    base_model: UploadFile = File(...),
    private: bool = Form(False),
    authorization: str = Header(None)
):
    expected_token = (ROOT / 'runtime/control/tokens.json').read_text() if (ROOT / 'runtime/control/tokens.json').exists() else '{}'
    tokens = json.loads(expected_token)
    cid = os.environ.get('NEXORA_CLIENT', 'client-a')
    
    if authorization != f"Bearer {tokens.get(cid, '')}":
        raise HTTPException(401, 'Invalid or missing service token')
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
