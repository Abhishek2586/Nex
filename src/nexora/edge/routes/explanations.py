import json
from fastapi import APIRouter, HTTPException
from nexora.edge.store import rows
from nexora.ml.train import Predictor
from nexora.edge.inference import get_predictor

router = APIRouter()

@router.get('/explanations/{pid}')
def explain(pid: str, model: str = 'neural'):
    if model not in ['neural', 'baseline']:
        raise HTTPException(422, 'Unknown model')
    for r in rows("SELECT body FROM events WHERE kind='prediction' ORDER BY rowid DESC LIMIT 500"):
        p = json.loads(r['body'])['payload']
        if p.get('prediction_id') == pid:
            predictor = get_predictor() if model == 'neural' else Predictor('baseline')
            if not predictor:
                raise HTTPException(503, 'Predictor not ready')
            return predictor.explain(p['features'])
    raise HTTPException(404, 'Prediction not found')
