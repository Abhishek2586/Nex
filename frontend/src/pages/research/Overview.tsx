import React from 'react';
import { api } from '../../api/client';
import { SCENARIOS } from '../../app/routes';

export function Overview({ mode, scenario, speed, setScenario, setSpeed, start, session, selected, refresh, events, activeModel, activePrompts, latest, pred, S }: any) {
  const act = async (fn: () => Promise<unknown>) => { try { await fn(); const new_s = await api('sessions'); if (S) S(new_s); await refresh(); } catch (e) { console.error(e); } };

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
}