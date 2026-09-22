import uuid
import json
from nexora.edge.store import rows, execute, event

def get_active_interventions(session_id):
    return [json.loads(r['body']) for r in rows('SELECT body FROM interventions WHERE session_id=:id', {'id': session_id})]

def is_intervention_active(session_id):
    actives = get_active_interventions(session_id)
    return any(i['status'] in ['offered', 'accepted'] for i in actives)

def evaluate_policy(s, i, posture, current_time_s):
    # Path A: Deterministic posture policy
    decision = {'result': 'no_action', 'reason_codes': ['no_sustained_context'], 'source_type': 'synthetic', 'event_time_s': current_time_s}
    
    if posture > 20:
        if s.get('posture_since') is None:
            s['posture_since'] = current_time_s
    else:
        s['posture_since'] = None
    
    posture_triggered = False
    if s.get('posture_since') is not None and current_time_s - s['posture_since'] >= 30:
        if is_intervention_active(s['id']) or current_time_s - s.get('last_prompt', -1000) < s.get('cooldown_posture', 120):
            decision.update(result='suppressed', reason_codes=['active_prompt_or_cooldown'])
        else:
            prompt = {'id': str(uuid.uuid4()), 'session_id': s['id'], 'type': 'posture', 'status': 'offered', 'text': 'Take a moment to adjust your posture if comfortable.', 'source': 'Synthetic', 'event_time_s': current_time_s}
            execute('INSERT INTO interventions VALUES(:id,:sid,:body)', {'id': prompt['id'], 'sid': s['id'], 'body': json.dumps(prompt)})
            s['last_prompt'] = current_time_s
            event(s, 'intervention', prompt)
            decision.update(result='triggered', reason_codes=['posture_above_20_for_30s'])
            posture_triggered = True

    # Path B: Model-driven stress-like policy
    # We evaluate this if posture didn't trigger
    if not posture_triggered and 'latest_prediction' in s and s['latest_prediction']:
        pred = s['latest_prediction']
        if pred.get('abstained') is not True and pred.get('probabilities'):
            import os
            from pathlib import Path
            registry_path = Path(os.environ.get('NEXORA_ROOT', Path(__file__).resolve().parents[3])) / 'models' / 'registry' / 'active.json'
            threshold = None
            if registry_path.exists():
                try:
                    active = json.loads(registry_path.read_text())
                    threshold = active.get('threshold')
                except Exception as e:
                    import logging
                    logging.warning(f"Failed to read threshold: {e}")
                    
            if threshold is None:
                import logging
                logging.warning("No threshold found in active model metadata. Safely abstaining from model interventions.")
                decision.update(result='no_action', reason_codes=['missing_active_model_threshold'])
                event(s, 'decision', decision)
                return decision

            if pred['probabilities'][1] > threshold:
                if s.get('model_evidence_since') is None:
                    s['model_evidence_since'] = current_time_s
                
                if current_time_s - s['model_evidence_since'] >= 30:
                    if pred.get('features') and pred['features'][8] > 0.35:
                        if decision['result'] == 'no_action':
                            decision.update(result='suppressed', reason_codes=['high_motion'])
                    elif is_intervention_active(s['id']) or current_time_s - s.get('last_prompt_breathing', -1000) < s.get('cooldown_breathing', 240):
                        if decision['result'] == 'no_action':
                            decision.update(result='suppressed', reason_codes=['active_prompt_or_cooldown_breathing'])
                    else:
                        prompt = {'id': str(uuid.uuid4()), 'session_id': s['id'], 'type': 'breathing', 'status': 'offered', 'text': 'Take a moment to breathe and reset.', 'source': 'Synthetic Model', 'event_time_s': current_time_s}
                        execute('INSERT INTO interventions VALUES(:id,:sid,:body)', {'id': prompt['id'], 'sid': s['id'], 'body': json.dumps(prompt)})
                        s['last_prompt_breathing'] = current_time_s
                        event(s, 'intervention', prompt)
                        decision.update(result='triggered', reason_codes=['model_sustained_evidence'])
            else:
                s['model_evidence_since'] = None
        else:
            s['model_evidence_since'] = None

    event(s, 'decision', decision)
    return decision
