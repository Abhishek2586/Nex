import pytest
import json
import time
from pathlib import Path
from nexora.edge.policy import evaluate_policy

def test_missing_threshold_fails_safely(tmp_path, monkeypatch):
    registry_path = tmp_path / 'models' / 'registry' / 'active.json'
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(json.dumps({})) # Missing threshold
    
    monkeypatch.setenv('NEXORA_ROOT', str(tmp_path))
    
    state = {'id': 'test-123', 'latest_prediction': {'abstained': False, 'probabilities': [0.1, 0.9]}}
    
    # 0.9 would normally trigger, but without threshold it defaults to 1.1, so it shouldn't trigger
    decision = evaluate_policy(state, None, 0, time.time())
    
    assert decision['result'] == 'no_action'
