"""
Edge inference module with tracked reload state.
Task 12: No silent failures. Exposes loaded_model_hash, reload_status, reload_error, last_reload_time.
"""
from nexora.ml.train import Predictor
from pathlib import Path
import json
import logging
import time

logger = logging.getLogger(__name__)

# Global predictor instance used by the edge service
predictor = None
_last_active_hash = None
_registry_path = Path('models/registry/active.json')

# Task 12: Tracked reload state
reload_status: str = "not_loaded"   # not_loaded | ok | failed | mismatch
reload_error: str | None = None
last_reload_time: float | None = None
loaded_model_hash: str | None = None
registry_model_hash: str | None = None


def get_predictor():
    global predictor, _last_active_hash, reload_status, reload_error, last_reload_time
    global loaded_model_hash, registry_model_hash

    if _registry_path.exists():
        try:
            active = json.loads(_registry_path.read_text())
            current_hash = active.get('model_hash')
            registry_model_hash = current_hash

            if current_hash != _last_active_hash:
                try:
                    new_predictor = Predictor()
                    predictor = new_predictor
                    _last_active_hash = current_hash
                    loaded_model_hash = current_hash
                    reload_status = "ok"
                    reload_error = None
                    last_reload_time = time.time()
                    logger.info("Predictor reloaded for model hash %s", current_hash[:8] if current_hash else "?")
                except Exception as exc:
                    # Task 12: Keep previous predictor if safe; expose mismatch clearly
                    reload_status = "failed"
                    reload_error = str(exc)
                    last_reload_time = time.time()
                    logger.error(
                        "Predictor reload failed for hash %s: %s — keeping previous predictor",
                        current_hash[:8] if current_hash else "?",
                        exc
                    )
                    # loaded_model_hash remains the previously loaded hash — do NOT update
        except Exception as exc:
            reload_status = "failed"
            reload_error = f"Could not read registry: {exc}"
            last_reload_time = time.time()
            logger.error("Failed to read active model registry: %s", exc)

    return predictor


def get_reload_state() -> dict:
    """Return the current reload tracking state for health reporting."""
    mismatch = (loaded_model_hash != registry_model_hash) and (registry_model_hash is not None)
    return {
        "loaded_model_hash": loaded_model_hash,
        "registry_model_hash": registry_model_hash,
        "reload_status": "mismatch" if mismatch and reload_status == "failed" else reload_status,
        "reload_error": reload_error,
        "last_reload_time": last_reload_time,
        "hash_mismatch": mismatch,
    }


def set_predictor(p):
    global predictor
    predictor = p


def init_predictor():
    global predictor, _last_active_hash, reload_status, reload_error, last_reload_time
    global loaded_model_hash, registry_model_hash
    try:
        predictor = Predictor()
        if _registry_path.exists():
            active = json.loads(_registry_path.read_text())
            h = active.get('model_hash')
            _last_active_hash = h
            loaded_model_hash = h
            registry_model_hash = h
        reload_status = "ok"
        reload_error = None
        last_reload_time = time.time()
    except FileNotFoundError:
        predictor = None
        reload_status = "not_loaded"
