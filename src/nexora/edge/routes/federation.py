import os
import re
import json
import datetime
import httpx
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Header
from fastapi.responses import FileResponse
from pathlib import Path
from nexora.edge.schemas import ExperimentRequest
from nexora.federation.client_worker import train_client

router = APIRouter()
ROOT = Path(__file__).resolve().parents[4]
_projection_cache: list[dict] = []
_projection_cache_key = None

def coordinator_request(method, path, **kwargs):
    base = os.environ.get('NEXORA_COORDINATOR_URL', 'http://127.0.0.1:8100')
    ca_file = os.environ.get('NEXORA_CA_FILE')
    expected_token = (ROOT / 'runtime/control/tokens.json').read_text() if (ROOT / 'runtime/control/tokens.json').exists() else '{}'
    tokens = json.loads(expected_token)
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f"Bearer {tokens.get('coordinator', '')}"
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

@router.post('/models/{run_id}/activate')
def activate_candidate(run_id: str, body: dict):
    try: 
        response = coordinator_request('POST', f'/api/v1/models/{run_id}/activate', json=body, timeout=2)
    except httpx.HTTPError: 
        raise HTTPException(503, 'Coordinator unavailable')
    if response.status_code != 200: 
        raise HTTPException(response.status_code, response.text)
    return response.json()

@router.post('/models/rollback')
def rollback_model():
    try: 
        response = coordinator_request('POST', '/api/v1/models/rollback', timeout=2)
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

@router.get('/evidence/export')
def export_evidence():
    """Task 14: Delegate to canonical evidence builder (same format as build_evidence.py)."""
    from nexora.evidence.builder import build_evidence_package
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    zip_filename = f'nexora-evidence-{timestamp}.zip'
    zip_path = ROOT / 'artifacts' / zip_filename
    build_evidence_package(ROOT, zip_path)
    return FileResponse(path=zip_path, filename=zip_filename, media_type='application/zip')


@router.get('/models/active')
def get_active_model():
    """Task 10: Dedicated endpoint - frontend uses this to get the active model without inference."""
    target_meta = ROOT / 'models' / 'registry' / 'active.json'
    if not target_meta.exists():
        raise HTTPException(404, 'No active model')
    from nexora.edge.inference import get_reload_state
    meta = json.loads(target_meta.read_text())
    
    # Task: include dataset_hash from manifest.windows_sha256 if available
    dataset_manifest_path = ROOT / 'data' / 'synthetic' / 'manifest.json'
    if dataset_manifest_path.exists():
        try:
            d_manifest = json.loads(dataset_manifest_path.read_text())
            meta['dataset_hash'] = d_manifest.get('windows_sha256')
        except Exception: pass
        
    reload_state = get_reload_state()
    meta['reload_state'] = reload_state
    return meta


_MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB hard limit on uploaded model


def _validate_run_id(run_id: str) -> None:
    """Validate run_id is UUID4 with no path traversal (Task 7)."""
    if not re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', run_id):
        raise HTTPException(400, 'run_id must be a valid UUID4')


def _validate_round_id(round_id: str) -> int:
    """Validate round_id is an integer 1-10 (Task 7)."""
    try:
        r = int(round_id)
    except (ValueError, TypeError):
        raise HTTPException(400, 'round_id must be an integer')
    if r < 1 or r > 10:
        raise HTTPException(400, 'round_id must be between 1 and 10')
    return r


@router.post('/train')
async def train(
    base_model: UploadFile = File(...),
    private: bool = Form(False),
    run_id: str = Form(...),
    round_id: str = Form(...),
    base_model_hash: str = Form(...),
    feature_schema_hash: str = Form(...),
    architecture_id: str = Form(...),
    client_id: str = Form(...),
    protocol_version: str = Form(...),
    authorization: str = Header(None)
):
    expected_token = (ROOT / 'runtime/control/tokens.json').read_text() if (ROOT / 'runtime/control/tokens.json').exists() else '{}'
    tokens = json.loads(expected_token)
    cid = os.environ.get('NEXORA_CLIENT', 'client-a')

    if authorization != f"Bearer {tokens.get(cid, '')}":
        raise HTTPException(401, 'Invalid or missing service token')
    if client_id != cid:
        raise HTTPException(400, 'Client ID mismatch with service environment')

    # Validate inputs before touching the filesystem (Task 7)
    _validate_run_id(run_id)
    validated_round = _validate_round_id(round_id)
    
    if protocol_version != 'nexora-fed-v1':
        raise HTTPException(400, f'Unsupported protocol_version: {protocol_version}')

    work_dir = ROOT / 'runtime' / cid / 'federation' / run_id
    work_dir.mkdir(parents=True, exist_ok=True)

    base_path = work_dir / 'base.safetensors'
    output_path = work_dir / 'output.safetensors'

    # Enforce upload size limit before writing to disk (Task 7)
    content_bytes = await base_model.read()
    if len(content_bytes) > _MAX_UPLOAD_BYTES:
        raise HTTPException(413, f'Base model upload exceeds {_MAX_UPLOAD_BYTES // 1024 // 1024} MB limit')
    base_path.write_bytes(content_bytes)

    try:
        metadata = train_client(cid, base_path, output_path, private, run_id, str(validated_round), base_model_hash, feature_schema_hash, architecture_id)
        metadata['protocol_version'] = protocol_version
    except Exception as e:
        raise HTTPException(500, f'Training failed: {str(e)}')

    if not output_path.exists():
        raise HTTPException(500, 'Output model missing')

    # Return the metadata and the trained model file
    response = FileResponse(path=output_path, media_type='application/octet-stream')
    response.headers['X-Federation-Metadata'] = json.dumps(metadata)
    return response
