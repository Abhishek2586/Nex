import json
import shutil
import tempfile
import time
from pathlib import Path
from nexora.edge.policy import evaluate_policy


def test_missing_threshold_returns_no_action_with_reason(monkeypatch):
    """When active.json has no threshold, policy must return no_action with reason
    'missing_active_model_threshold' and must NOT trigger an intervention."""
    tmp = Path(tempfile.mkdtemp(prefix='nexora-policy-test-'))
    try:
        registry_path = tmp / 'models' / 'registry' / 'active.json'
        registry_path.parent.mkdir(parents=True)
        registry_path.write_text(json.dumps({}))  # threshold field absent

        monkeypatch.setenv('NEXORA_ROOT', str(tmp))

        # probability[1] = 0.9 would normally trigger if threshold were 0.5
        state = {
            'id': 'test-123',
            'latest_prediction': {'abstained': False, 'probabilities': [0.1, 0.9]},
        }

        decision = evaluate_policy(state, None, 0, time.time())

        assert decision['result'] == 'no_action', (
            f"Expected no_action, got {decision['result']!r}"
        )
        assert 'missing_active_model_threshold' in decision.get('reason_codes', []), (
            f"Expected reason_codes to contain 'missing_active_model_threshold', "
            f"got {decision.get('reason_codes')}"
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
