import os
import httpx
from fastapi import APIRouter
from nexora.edge.inference import get_predictor
from nexora.edge.store import CLIENT

router = APIRouter()

@router.get('/health')
def health():
    coordinator_url = os.environ.get('NEXORA_COORDINATOR_URL', 'http://127.0.0.1:8100')
    ca_file = os.environ.get('NEXORA_CA_FILE')
    predictor = get_predictor()
    try:
        response = httpx.get(f'{coordinator_url}/health', timeout=0.25, verify=ca_file or True)
        coordinator = 'available' if response.status_code == 200 else 'unavailable'
    except httpx.HTTPError:
        coordinator = 'unavailable'
    return {
        'client_id': CLIENT,
        'status': 'available',
        'model_ready': predictor is not None,
        'transport': 'TLS verified' if ca_file else 'Local HTTP',
        'source': 'Synthetic',
        'coordinator': coordinator,
        'local_inference_during_outage': predictor is not None
    }
