import os
from pathlib import Path

root = Path("frontend/src")

files = {
    "pages/research/Overview.tsx": """import React from 'react';
import { api } from '../../api/client';
import { SCENARIOS } from '../../app/routes';

export function Overview({ mode, scenario, speed, setScenario, setSpeed, start, session, selected, refresh, events, activeModel, activePrompts, latest, pred }: any) {
  const act = async (fn: () => Promise<unknown>) => { try { await fn(); await refresh(); } catch (e) { console.error(e); } };

  return (
    <>
      <div className="card">
        <h2>Prototype Summary</h2>
        <p><b>NEXORA</b> is a privacy-aware software-in-the-loop research prototype for stress-aware, posture-aware, and context-aware digital interventions.</p>
        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
          <span className="badge">Software-in-the-loop</span><span className="badge">Synthetic Data</span>
        </div>
      </div>
      <div className="card controls">
        <div style={{ flexBasis: '100%', marginBottom: '10px' }}>
          <h2>Session Control</h2>
          <p className="muted">Start a simulated session to inject synthetic physiological and biomechanical signals into the processing pipeline.</p>
        </div>
        <label>Scenario<select value={scenario} onChange={e => setScenario(e.target.value)}>{Object.entries(SCENARIOS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
        <label>Replay speed<select value={speed} onChange={e => setSpeed(+e.target.value)}>{[1, 5, 20].map(x => <option key={x} value={x}>{x}×</option>)}</select></label>
        <button onClick={start}>Start synthetic session</button>
        <button className="secondary" disabled={!session || session.status === 'stopped'} onClick={() => act(() => api(`sessions/${selected}/${session?.status === 'running' ? 'pause' : 'start'}`, {}))}>{session?.status === 'running' ? 'Pause' : 'Resume'}</button>
        <button className="secondary" disabled={!session || session.status === 'stopped'} onClick={() => act(() => api(`sessions/${selected}/stop`, {}))}>Stop</button>
      </div>
      <div className="card">
        <h2>Architecture Pipeline</h2>
        <div className="pipeline-container">
          <div className="pipeline-node"><div className="node-icon">📥</div><b>Input</b><small>{latest ? 'Synthetic' : 'WESAD unavailable'}</small></div>
          <div className="pipeline-node"><div className="node-icon">🔍</div><b>Quality</b><small>{pred?.abstained ? 'missing/high-motion' : 'good'}</small></div>
          <div className="pipeline-node"><div className="node-icon">⚙️</div><b>Features</b><small>12 features</small></div>
          <div className="pipeline-node"><div className="node-icon">🧠</div><b>Model</b><small>{activeModel ? activeModel.model_hash?.slice(0, 8) : 'None'}</small></div>
          <div className="pipeline-node"><div className="node-icon">⚖️</div><b>Policy</b><small>Threshold {activeModel?.threshold != null ? activeModel.threshold : "Unavailable"}</small></div>
          <div className="pipeline-node"><div className="node-icon">💬</div><b>Intervention</b><small>{activePrompts.length ? 'Offered' : 'None'}</small></div>
          <div className="pipeline-node"><div className="node-icon">📈</div><b>Learning</b><small>{events.filter((e:any) => e.event_type === 'feedback').at(-1)?.payload.action || 'None'}</small></div>
        </div>
      </div>
      <div className="twocol">
        <div className="card">
          <h2>Session Summary</h2>
          <p>Active session ID: <b>{selected || 'None'}</b></p>
          <p>Scenario: {scenario}</p>
          <p className="status">Status: <span className="badge">{session?.status || 'Unknown'}</span></p>
          <p>Active model: {activeModel?.model_hash?.slice(0, 8) || 'None'}</p>
          <p>Reviewer next step: Go to <b>Live session</b> to see real-time signals.</p>
        </div>
        <div className="card">
          <h2>Prototype Limitations & Hardware</h2>
          <p><b>Important:</b> This is a local software simulation. No clinical claims are made.</p>
          <p><b>Future Embodiment:</b> Wrist-worn sensing unit (EDA, Temp, IMU) + optional posture accessory (back clip).</p>
          <p>Current state uses purely synthetic or replayed inputs.</p>
        </div>
      </div>
    </>
  );
}""",

    "pages/research/LiveSession.tsx": """import React from 'react';
import { SCENARIOS } from '../../app/routes';
import { MetricCard } from '../../components/MetricCard';
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

export function LiveSession({ selected, scenario, session, speed, activeModel, pred, activePrompts, latest, obs, events }: any) {
  const renderChart = (title: string, dataKey: string, unit: string, stroke: string) => (
    <div className="card">
      <div className="cardtitle"><h2>{title}</h2><span>Synthetic · {unit}</span></div>
      <ResponsiveContainer width="100%" height={150}>
        <LineChart data={obs.filter((_:any,i:number) => i % 4 === 0)}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="event_time_s" unit="s" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey={dataKey} stroke={stroke} dot={false} isAnimationActive={false} connectNulls={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  return (
    <>
      <div className="info-strip">
        <span><b>Session:</b> {selected?.slice(0, 8) || 'None'}</span>
        <span><b>Scenario:</b> {SCENARIOS[scenario]}</span>
        <span><b>Speed:</b> {session?.speed || speed}×</span>
        <span><b>Model:</b> {activeModel?.model_hash?.slice(0, 8) || 'None'}</span>
        <span><b>Threshold:</b> {activeModel?.threshold || 'N/A'}</span>
        <span><b>Policy:</b> {pred?.abstained ? 'Abstained' : 'Active'}</span>
        <span><b>Intervention:</b> {activePrompts.length ? 'Offered' : 'None'}</span>
      </div>
      <div className="stats">
        <MetricCard title="EDA" value={latest?.eda_us} unit="µS" />
        <MetricCard title="Skin Temp" value={latest?.skin_temperature_c} unit="°C" />
        <MetricCard title="Posture" value={latest?.posture_angle_deg} unit="°" />
        <MetricCard title="Movement" value={latest?.acc_mag_g} unit="g" />
      </div>
      <div className="twocol">
        {renderChart('Electrodermal activity (EDA)', 'eda_us', 'µS', '#087f83')}
        {renderChart('Posture Angle', 'posture_angle_deg', '°', '#d35400')}
      </div>
      <div className="twocol">
        {renderChart('Skin Temperature', 'skin_temperature_c', '°C', '#c0392b')}
        {renderChart('Acceleration Magnitude (Movement)', 'acc_mag_g', 'g', '#8e44ad')}
      </div>
      <div className="twocol">
        <div className="card">
          <h2>Model State & Current Interpretation</h2>
          <div className="model-score-display">{!pred ? 'Waiting for a complete 30-second window' : pred.abstained ? `Abstained: ${pred.reason}` : `Stress model score: ${(pred.probabilities[1] * 100).toFixed(1)}%`}</div>
          <p className="muted">Scores are uncalibrated model outputs indicating autonomic arousal likelihood. Not a medical diagnosis.</p>
          {activeModel?.model_hash && (activeModel?.reload_state?.hash_mismatch || !['loaded', 'ok', 'ready'].includes(activeModel?.reload_state?.reload_status)) && (
            <div className="alert-box" style={{ background: '#f8d7da', color: '#721c24', padding: '0.5rem', marginTop: '0.5rem', borderRadius: '6px' }}>
              Warning: Reload Issue. Status: {activeModel.reload_state?.reload_status || 'unknown'}. {activeModel.reload_state?.reload_error && `Error: ${activeModel.reload_state.reload_error}`}. {activeModel.reload_state?.hash_mismatch ? `Hash mismatch (loaded: ${activeModel.reload_state?.loaded_model_hash?.slice(0, 8) || 'none'} vs registry: ${activeModel.reload_state?.registry_model_hash?.slice(0, 8)})` : ''}
            </div>
          )}
          <div style={{ display: 'flex', gap: '10px', marginTop: '15px', flexWrap: 'wrap' }}>
            <div className="help-box"><b>Predicted vs Abstained:</b> The policy engine skips inference if signal quality is poor (e.g., high motion).</div>
            <div className="help-box"><b>Threshold:</b> The cutoff score ({activeModel?.threshold || 'N/A'}) to trigger an intervention consideration.</div>
          </div>
        </div>
        <div className="card">
          <h2>Recent Predictions</h2>
          <table className="data-table">
            <thead><tr><th>Time</th><th>Source</th><th>Status</th><th>Score / Reason</th></tr></thead>
            <tbody>
              {events.filter((e:any) => e.event_type === 'prediction').slice(-5).reverse().map((e:any) => (
                <tr key={e.event_id}>
                  <td>{new Date(e.created_at).toLocaleTimeString([], { hour12: false })}</td>
                  <td>{e.payload.source}</td>
                  <td><span className={`badge ${e.payload.abstained ? 'badge-abstained' : ''}`}>{e.payload.abstained ? 'Abstained' : 'Predicted'}</span></td>
                  <td>{e.payload.abstained ? e.payload.reason : <b>{(e.payload.probabilities[1] * 100).toFixed(1)}%</b>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h2>Recent Decisions & Interventions</h2>
          <div className="timeline-container">
            {events.filter((e:any) => e.event_type === 'decision').slice(-5).reverse().map((e:any) => (
              <div className="timeline-row" key={e.event_id}>
                <div className="timeline-time">{new Date(e.created_at).toLocaleTimeString([], { hour12: false })}</div>
                <div className="timeline-content"><b>{e.payload.result === 'intervention_triggered' ? 'Triggered Intervention' : 'Suppressed'}</b> <span className="muted">{e.payload.reason_codes.join(', ')}</span></div>
              </div>
            ))}
            {events.filter((e:any) => e.event_type === 'decision').length === 0 && <p className="muted">No decisions logged yet.</p>}
          </div>
        </div>
      </div>
    </>
  );
}""",

    "pages/research/Interventions.tsx": """import React from 'react';
import { api } from '../../api/client';

export function Interventions({ prompts, act }: any) {
  return (
    <div className="card">
      <h2>Prompts & feedback</h2>
      <p className="page-note">Physical hardware outputs are not connected in this software-only prototype. Interventions are delivered to the Participant App.</p>
      {!prompts.length && <p>No prompts yet. Start a session and induce stress-like conditions to exercise the policy engine.</p>}
      <div className="intervention-list">
        {prompts.map((p:any) => (
          <article className="intervention-card" key={p.id}>
            <div className="intervention-header">
              <span className={`badge badge-${p.status}`}>{p.status}</span>
              <span className="muted">{new Date(p.created_at).toLocaleString()}</span>
            </div>
            <h3>{p.text}</h3>
            <div className="intervention-meta">
              <span><b>Source:</b> {p.source}</span>
              <span><b>Context:</b> Model threshold exceeded, contextual checks passed.</span>
            </div>
            <div className="intervention-actions">
              {(p.status === 'offered' ? ['accept', 'dismiss'] : p.status === 'accepted' ? ['complete', 'cancel'] : []).map(action => (
                <button key={action} className={action === 'dismiss' || action === 'cancel' ? 'secondary' : ''} onClick={() => act(() => api(`interventions/${p.id}/feedback`, { feedback_id: crypto.randomUUID(), action }))}>{action}</button>
              ))}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}""",

    "pages/research/AIInsights.tsx": """import React, { useState } from 'react';
import { api } from '../../api/client';
import { ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ReferenceLine, Bar } from 'recharts';

export function AIInsights({ health, models, pred, act, refresh }: any) {
  const [selectedDataset, SD] = useState('synthetic');
  const [explainModel, XM] = useState('neural');
  const [explanation, X] = useState<any>(null);

  return (
    <>
      <div className="card">
        <h2>Dataset Insights</h2>
        <label style={{ marginRight: '10px' }}>Dataset:
          <select value={selectedDataset} onChange={e => SD(e.target.value)}>
            <option value="synthetic">Synthetic</option>
            {health.wesad && health.wesad.status === 'COMPLETED' && <option value="wesad">WESAD</option>}
          </select>
        </label>
      </div>
      <div className="twocol">
        {models.filter((m:any) => (selectedDataset === 'wesad' ? m.source === 'Recorded dataset' : m.source === 'Synthetic')).map((m:any) => (
          <div className="card" key={m.model_hash}>
            <span className="badge">{m.source} · {m.lifecycle_state || 'candidate'}</span>
            <h2>{m.model_id === 'baseline' ? 'Random forest' : 'Neural network'}</h2>
            <strong className="metric">{(100 * (m.validation_score || m.metrics?.balanced_accuracy || 0)).toFixed(1)}%</strong>
            <p>Validation Balanced accuracy</p>
            <p>Test Balanced Acc: {(100 * (m.test_balanced_accuracy || m.metrics?.balanced_accuracy || 0)).toFixed(1)}% · Macro-F1: {(m.test_macro_f1 || m.metrics?.macro_f1 || 0).toFixed(3)}</p>
            <p>Architecture: {m.architecture_id || 'Unavailable'}</p>
            <p>Hash: {m.model_hash}</p>
            <p>Dataset Hash: {m.dataset_hash}</p>
            <div>
              <h4>Confusion Matrix</h4>
              <table style={{ width: '100%', textAlign: 'center' }}>
                <thead><tr><th>Actual \\ Pred</th><th>Baseline</th><th>Stress-like</th></tr></thead>
                <tbody>
                  <tr><td>Baseline</td><td>{m.metrics?.confusion_matrix?.[0]?.[0]}</td><td>{m.metrics?.confusion_matrix?.[0]?.[1]}</td></tr>
                  <tr><td>Stress-like</td><td>{m.metrics?.confusion_matrix?.[1]?.[0]}</td><td>{m.metrics?.confusion_matrix?.[1]?.[1]}</td></tr>
                </tbody>
              </table>
            </div>
            <div className="alert-box" style={{ marginTop: '1rem', padding: '1rem', background: '#ffeeba', color: '#856404' }}>
              <strong>{m.source === 'Recorded dataset' ? 'Recorded WESAD research dataset result — offline evaluation only. This model is not currently live in the simulator.' : 'Synthetic simulator result only'}</strong>
            </div>
          </div>
        ))}
      </div>
      <div className="card">
        <h2>Per-prediction attribution</h2>
        <label>Model (Live session explanation)
          <select value={explainModel} onChange={e => { XM(e.target.value); X(null); }}>
            <option value="neural">Neural network</option>
            <option value="baseline">Random forest</option>
          </select>
        </label>
        <button disabled={!pred?.prediction_id} onClick={() => act(async () => X(await api(`explanations/${pred.prediction_id}?model=${explainModel}`)))}>Explain latest prediction</button>
        {explanation && (
          <>
            <p>{explanation.method} · {explanation.output_space} · class {explanation.class}</p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={explanation.values.map((v: number, i: number) => ({ name: explanation.feature_names[i], value: v }))} layout="vertical" margin={{ left: 50 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip />
                <ReferenceLine x={0} stroke="#000" />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
            <p>Completeness delta: {(explanation.convergence_delta ?? explanation.completeness_delta).toFixed(7)}</p>
            <p className="muted">Attribution describes model behaviour, not causality or clinical effect.</p>
          </>
        )}
      </div>
    </>
  );
}"""
}

for filepath, content in files.items():
    p = root / filepath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    
print("Created Overview, LiveSession, Interventions, AIInsights")
