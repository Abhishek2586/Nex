import asyncio
import json
import time
import numpy as np
import uuid
from nexora.edge.store import rows, save, event
from nexora.edge.inference import get_predictor
from nexora.edge.policy import evaluate_policy
from nexora.data.synthetic import generate_subject
from nexora.features.extract import extract, HIGH_MOTION_STD_THRESHOLD

async def replay_task():
    while True:
        for row in rows('SELECT body FROM sessions'):
            s = json.loads(row['body'])
            if s['status'] != 'running': continue
            samples, labels, posture = generate_subject(0, s['seed'], scenario=s['scenario'])
            
            # Pre-generate heart rate array: 68 bpm baseline, correlated with posture/stress
            _rng_hr = np.random.default_rng(s['seed']+99999)
            hr_array = np.clip(68.0 + 0.6 * posture + _rng_hr.normal(0, 2.5, len(posture)), 45.0, 130.0).round(1)
            
            for _ in range(s.get('speed', 5)):
                i = s.get('index', 0)
                if i >= len(samples): 
                    s['status'] = 'stopped'
                    break
                
                values = samples[i]
                current_time_s = i / 4.0
                obs = {
                    'event_time_s': current_time_s,
                    'source_type': 'synthetic',
                    'source_label': 'Synthetic',
                    'signals': {key: None if not np.isfinite(v) else float(v) for key, v in zip(['eda_us', 'skin_temperature_c', 'acc_x_g', 'acc_y_g', 'acc_z_g'], values)},
                    'heart_rate_bpm': float(hr_array[i]),
                    'posture_angle_deg': float(posture[i])
                }
                event(s, 'observation', obs)
                
                # Check for window ready every 30s (120 samples)
                if i >= 119:
                    feat = extract(samples[i-119:i+1])
                    event(s, 'window_ready', feat)
                    if feat['values'] is None:
                        pred = {'prediction_id': str(uuid.uuid4()), 'abstained': True, 'reason': feat['reason'], 'source': 'Synthetic'}
                        event(s, 'prediction', pred)
                        s['latest_prediction'] = pred
                    elif feat['values'][8] > HIGH_MOTION_STD_THRESHOLD:
                        pred = {'prediction_id': str(uuid.uuid4()), 'abstained': True, 'reason': 'Signal quality is insufficient (high motion)', 'source': 'Synthetic'}
                        event(s, 'prediction', pred)
                        s['latest_prediction'] = pred
                    else:
                        predictor = get_predictor()
                        if predictor:
                            started = time.perf_counter()
                            p = predictor.predict(feat['values'])[0]
                            pred = {
                                'prediction_id': str(uuid.uuid4()),
                                'abstained': False,
                                'probabilities': p.tolist(),
                                'predicted_class': int(p.argmax()),
                                'model_id': 'neural',
                                'model_hash': predictor.metadata['model_hash'],
                                'inference_ms': (time.perf_counter() - started) * 1000,
                                'features': feat['values'],
                                'source': 'Synthetic'
                            }
                            event(s, 'prediction', pred)
                            s['latest_prediction'] = pred
                
                if i % 20 == 0:
                    evaluate_policy(s, i, posture[i], current_time_s)
                
                s['index'] += 1
            save(s)
        await asyncio.sleep(0.25)
