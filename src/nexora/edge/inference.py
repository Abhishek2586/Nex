from nexora.ml.train import Predictor
from pathlib import Path
import json

# Global predictor instance used by the edge service
predictor = None
_last_active_hash = None
_registry_path = Path('models/registry/active.json')

def get_predictor():
    global predictor, _last_active_hash
    if _registry_path.exists():
        try:
            active = json.loads(_registry_path.read_text())
            current_hash = active.get('model_hash')
            if current_hash != _last_active_hash:
                predictor = Predictor()
                _last_active_hash = current_hash
        except: pass
    return predictor

def set_predictor(p):
    global predictor
    predictor = p

def init_predictor():
    global predictor, _last_active_hash
    try: 
        predictor = Predictor()
        if _registry_path.exists():
            _last_active_hash = json.loads(_registry_path.read_text()).get('model_hash')
    except FileNotFoundError: 
        predictor = None
