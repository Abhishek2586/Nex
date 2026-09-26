import os
from pathlib import Path

root = Path("frontend/src")

files = {
    "pages/research/FederatedLab.tsx": """import React from 'react';
import { api } from '../../api/client';
import { Row } from '../../types';

export function FederatedLab({ health, jobs, privacy, runs, fedDisabled, fedReason, act }: any) {
  return (
    <>
      <div className="card explanation-card">
        <h2>Why Federated Learning?</h2>
        <p>To improve the global stress-inference model without centralizing sensitive physiological data (EDA, Temp), NEXORA learns locally on the edge and aggregates model updates (not raw data). <i>Note: This prototype simulates federated nodes as local processes on the same machine. Secure Aggregation is out of scope for this build.</i></p>
      </div>
      <div className="card controls">
        <button disabled={fedDisabled} onClick={() => act(() => api('experiment-jobs', { mode: 'federated', rounds: 1, dataset: 'synthetic' }))}>Run 1-round FedAvg</button>
        <button disabled={fedDisabled} onClick={() => act(() => api('experiment-jobs', { mode: 'federated', rounds: 3, dataset: 'synthetic' }))}>Run 3-round FedAvg</button>
        <button disabled={fedDisabled} onClick={() => act(() => api('experiment-jobs', { mode: 'federated', rounds: 5, dataset: 'synthetic' }))}>Run 5-round FedAvg</button>
        <button disabled={fedDisabled} onClick={() => act(() => api('experiment-jobs', { mode: 'private-federated', rounds: 1, dataset: 'synthetic' }))}>Run Private FedAvg (DP)</button>
        <span className={`badge ${health.coordinator === 'available' ? 'badge-success' : 'badge-error'}`}>Coordinator {health.coordinator}</span>
        {fedDisabled && <span className="muted" style={{ marginLeft: '0.5rem' }}>{fedReason}</span>}
      </div>
      <div className="card">
        <h2>Client Topology</h2>
        <p className="muted">Three isolated processes on the same host representing independent edge devices.</p>
        <div className="topology-diagram">
          {['client-a', 'client-b', 'client-c'].map(cid => {
            const priv = privacy.find((v:any) => v.client_id === cid);
            return (
              <div className="topology-node" key={cid}>
                <b className="node-title">{cid}</b><small>Port {cid === 'client-a' ? 8080 : cid === 'client-b' ? 8082 : 8083}</small>
                {priv ? <div className="dp-info"><small>ε {priv.epsilon.toFixed(2)}</small><br /><small>{priv.steps} DP steps</small></div> : <div className="dp-info empty">No DP data</div>}
              </div>
            );
          })}
        </div>
        <div className="topology-arrow">↕ HTTP (loopback)</div>
        <div className="topology-coordinator"><b>Central Coordinator</b><small>Port 8100 · FedAvg aggregation</small></div>
      </div>
      {jobs.length > 0 && (
        <div className="card">
          <h2>Experiment jobs</h2>
          {jobs.slice(0, 5).map((j:any) => (
            <div className="row" key={j.job_id}>
              <span>{j.mode} · {j.rounds} round · {j.status}</span>
              <span>{j.job_id.slice(0, 8)} {['queued', 'training'].includes(j.status) && <button onClick={() => act(() => api(`experiment-jobs/${j.job_id}/cancel`, {}))}>Cancel</button>}</span>
            </div>
          ))}
        </div>
      )}
      <div className="stats">
        {privacy.map((v:any) => (
          <div className="card" key={v.client_id}>
            <small>{v.client_id} · same laptop</small>
            <strong>ε {v.epsilon.toFixed(3)}</strong>
            <span>δ {v.delta} · {v.steps} steps</span>
            <p className="muted">{v.accountant} · {v.randomness_mode.replaceAll('_', ' ')}</p>
          </div>
        ))}
      </div>
      <div className="card">
        <h2>Measured experiment runs</h2>
        {!runs.length && <p>No completed distributed run.</p>}
        {runs.map((r:any) => (
          <article key={r.run_id}>
            <span className="badge">{r.mode} · {r.source} · {r.status}</span>
            <h3>{r.rounds.length} round{r.rounds.length === 1 ? '' : 's'} · val. score {(r.validation_score * 100 || 0).toFixed(1)}%</h3>
            <p>Run {r.run_id}</p>
            <p>Candidate Hash: {r.model_hash}</p>
            <button onClick={() => act(() => api(`models/${r.run_id}/activate`, { round: r.rounds.length }))}>Activate Candidate</button>
            <button className="secondary" style={{ marginLeft: '0.5rem' }} onClick={() => act(() => api(`models/rollback`, {}))}>Rollback to Previous</button>
            {r.rounds.map((round: Row) => (
              <div className="row" key={round.round}>
                <span>Round {round.round}: {round.clients.map((c: Row) => `${c.client_id} ${c.records} records`).join(' · ')}</span>
                <b>Base: {round.base_hash?.slice(0, 8)}... Update: {round.model_hash?.slice(0, 8)}...</b>
              </div>
            ))}
          </article>
        ))}
      </div>
    </>
  );
}""",

    "pages/research/Evidence.tsx": """import React from 'react';

export function Evidence({ health, models, activeModel }: any) {
  const exportEvidence = () => { window.location.href = '/api/v1/evidence/export'; };

  return (
    <div className="card">
      <h2>Evidence package</h2>
      {health.wesad && health.wesad.status === 'COMPLETED' ? (
        <div style={{ background: 'var(--surface)', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1rem' }}>
          <p><strong>WESAD offline evaluation:</strong> COMPLETED</p>
          <p><strong>Imported subjects:</strong> {health.wesad.subject_count}</p>
          <p><strong>Train / Val / Test split counts:</strong> {health.wesad.splits.train?.length} / {health.wesad.splits.validation?.length} / {health.wesad.splits.test?.length}</p>
          <p><strong>Dataset SHA256:</strong> {health.wesad.dataset_hash}</p>
          <p><strong>Baseline model hash:</strong> {models.find((m:any) => m.model_id === 'baseline' && m.source === 'Recorded dataset')?.model_hash?.slice(0, 8) || 'N/A'}</p>
          <p><strong>Neural model hash:</strong> {models.find((m:any) => m.model_id === 'neural' && m.source === 'Recorded dataset')?.model_hash?.slice(0, 8) || 'N/A'}</p>
          <p><strong>Measured test metrics (Baseline):</strong> Balanced Acc: {((models.find((m:any) => m.model_id === 'baseline' && m.source === 'Recorded dataset')?.test_balanced_accuracy || 0) * 100).toFixed(1)}% · Macro-F1: {(models.find((m:any) => m.model_id === 'baseline' && m.source === 'Recorded dataset')?.test_macro_f1 || 0).toFixed(3)}</p>
          <p><strong>Measured test metrics (Neural):</strong> Balanced Acc: {((models.find((m:any) => m.model_id === 'neural' && m.source === 'Recorded dataset')?.test_balanced_accuracy || 0) * 100).toFixed(1)}% · Macro-F1: {(models.find((m:any) => m.model_id === 'neural' && m.source === 'Recorded dataset')?.test_macro_f1 || 0).toFixed(3)}</p>
          <p><strong>Federated run status:</strong> {health.wesad.federated_status}</p>
          <p><strong>Private federated run status:</strong> {health.wesad.private_federated_status}</p>
        </div>
      ) : (
        <div style={{ background: 'var(--surface)', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1rem' }}>
          <p><strong>WESAD offline evaluation:</strong> NOT RUN</p>
        </div>
      )}
      <div style={{ background: 'var(--surface)', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1rem' }}>
        <p><strong>Active model:</strong> {activeModel ? activeModel.model_hash?.slice(0, 8) || 'None' : 'No active model'}</p>
        <p><strong>Architecture:</strong> {activeModel?.architecture_id || 'Unavailable'}</p>
        <p><strong>Threshold:</strong> {activeModel?.threshold != null ? activeModel.threshold : 'Unavailable'}</p>
        <p><strong>Lifecycle:</strong> {activeModel?.lifecycle_state || 'Unavailable'}</p>
        <p><strong>Source:</strong> Synthetic dataset (seeded, artificial)</p>
        <p><strong>Verification:</strong> Hash-indexed; see export-manifest.json inside ZIP</p>
      </div>
      <button onClick={exportEvidence} id="download-evidence-zip">Download ZIP Evidence</button>
    </div>
  );
}""",

    "pages/Settings.tsx": """import React from 'react';

export function Settings({ speed, setSpeed, activeModel }: any) {
  return (
    <div className="card">
      <h2>Settings</h2>
      <p className="muted">These settings apply to this browser session only.</p>
      <label style={{ display: 'block', marginBottom: '1rem' }}>Replay speed (applies to next session start)
        <select value={speed} onChange={e => setSpeed(+e.target.value)}>
          <option value={1}>1× (slow)</option>
          <option value={5}>5× (medium)</option>
          <option value={20}>20× (fast)</option>
        </select>
      </label>
      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <input type="checkbox" id="reduced-motion" onChange={e => { if (e.target.checked) { document.body.classList.add('reduce-motion') } else { document.body.classList.remove('reduce-motion') } }} aria-label="Reduce animations" />
        <span>Reduce animations (accessibility)</span>
      </label>
      <div className="muted" style={{ fontSize: '0.8rem', marginTop: '1rem' }}>
        <p>Active model hash: {activeModel?.model_hash?.slice(0, 8) || 'None'}</p>
        <p>Threshold: {activeModel?.threshold != null ? activeModel.threshold : 'Unavailable'}</p>
        <p>Architecture: {activeModel?.architecture_id || 'Unavailable'}</p>
      </div>
    </div>
  );
}""",
    
    "pages/participant/Home.tsx": """import React from 'react';
import { api } from '../../api/client';

export function Home({ session, pred, activePrompts, latest, start, act, selected }: any) {
  return (
    <>
      <div className="participant-hero">
        <span className="eyebrow">Desk-Work Wellbeing Assistant</span>
        <h2>{session?.status === 'running' ? 'Monitoring simulation is active' : session?.status === 'paused' ? 'Monitoring simulation is paused' : 'Ready to start a monitoring simulation'}</h2>
        <p>{pred?.abstained ? 'Signal quality is insufficient (e.g. high motion).' : activePrompts.length ? 'NEXORA has a small wellness suggestion for you.' : 'This prototype watches simulated physiological signals and offers gentle posture and stress guidance.'}</p>
        <span className="badge" style={{ background: 'rgba(255,255,255,0.2)' }}>Software-in-the-loop Prototype</span>
      </div>
      <div className="stats participant-signals">
        {[['EDA (Stress)', latest?.eda_us, 'available'], ['Skin Temperature', latest?.skin_temperature_c, 'available'], ['Posture Angle', latest?.posture_angle_deg, 'available']].map(([name, value, state]) => (
          <div className="card" key={String(name)}>
            <small>{name}</small>
            <strong>{value == null ? 'Unavailable' : 'Active'}</strong>
            <span>{state === 'available' ? 'Simulated Sensor' : 'Not supplied by this demo'}</span>
          </div>
        ))}
      </div>
      <div className="card controls">
        <button onClick={start}>Start Session</button>
        <button className="secondary" disabled={!session || session.status === 'stopped'} onClick={() => act(() => api(`sessions/${selected}/${session?.status === 'running' ? 'pause' : 'start'}`, {}))}>{session?.status === 'running' ? 'Pause' : 'Resume'}</button>
        <button className="secondary" disabled={!session || session.status === 'stopped'} onClick={() => act(() => api(`sessions/${selected}/stop`, {}))}>End session</button>
      </div>
    </>
  );
}""",

    "pages/participant/Guidance.tsx": """import React from 'react';
import { api } from '../../api/client';

export function Guidance({ activePrompts, act }: any) {
  return (
    <div className="card guidance">
      <h2>Current guidance</h2>
      {!activePrompts.length && <p className="calm-text">No action is needed right now. Continue your work comfortably.</p>}
      {activePrompts.map((p:any) => (
        <article key={p.id}>
          <span className="badge">Optional wellness suggestion</span>
          <h3>{p.text}</h3>
          <p>Take a moment to reset. You remain in control of your workflow.</p>
          <div className="intervention-actions">
            {(p.status === 'offered' ? ['accept', 'dismiss'] : p.status === 'accepted' ? ['complete', 'cancel'] : []).map(action => (
              <button key={action} className={action === 'dismiss' || action === 'cancel' ? 'secondary' : ''} onClick={() => act(() => api(`interventions/${p.id}/feedback`, { feedback_id: crypto.randomUUID(), action }))}>{action === 'complete' ? 'Done' : action === 'accept' ? 'Start' : action === 'dismiss' ? 'Not now' : action}</button>
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}""",

    "pages/participant/History.tsx": """import React from 'react';
import { SCENARIOS } from '../../app/routes';

export function History({ sessions, selected, events, SEL }: any) {
  return (
    <div className="card">
      <h2>Session history</h2>
      <p className="muted">Your sessions are retained only in local storage.</p>
      {!sessions.length && <p>No sessions yet. Start a session from the Home page.</p>}
      <div className="history-list">
        {sessions.map((s:any) => (
          <article key={s.id} className={`history-card ${s.id === selected ? 'active' : ''}`} onClick={() => SEL(s.id)}>
            <div className="history-header">
              <span className="badge">{SCENARIOS[s.scenario] || s.scenario}</span>
              <span className="badge">{s.status}</span>
            </div>
            <h3>Session {s.id.slice(0, 8)}</h3>
            <div className="history-meta">
              <span>{new Date(s.created_at).toLocaleString()}</span>
              {s.status === 'stopped' && <span>Duration: {s.started_at && s.stopped_at ? ((new Date(s.stopped_at).getTime() - new Date(s.started_at).getTime()) / 1000).toFixed(0) + 's' : '—'}</span>}
            </div>
            <p className="history-stats">{events.filter((e:any) => e.session_id === s.id && e.event_type === 'prediction').length} predictions · {events.filter((e:any) => e.session_id === s.id && e.event_type === 'feedback').length} feedback events</p>
          </article>
        ))}
      </div>
    </div>
  );
}""",

    "pages/participant/About.tsx": """import React from 'react';
export function About() {
  return (
    <div className="card">
      <h2>About this prototype</h2>
      <p>NEXORA is a privacy-aware research prototype demonstrating edge-based machine learning for digital wellness interventions.</p>
      <p><b>Prototype Scope:</b></p>
      <ul>
        <li>Local software-only simulation.</li>
        <li>Uses synthetic or replayed data.</li>
        <li>Not a medical device.</li>
        <li>No clinical validation or claims.</li>
        <li>Future hardware embodiment (wrist-worn sensor) is simulated in this build.</li>
      </ul>
    </div>
  );
}""",
    
    "pages/research/SystemEmbodiment.tsx": """import React from 'react';

export function SystemEmbodiment() {
  return (
    <div className="card">
      <h2>System & Embodiment</h2>
      <p>Details about the physical hardware embodiment and system design to be added.</p>
    </div>
  );
}"""
}

for filepath, content in files.items():
    p = root / filepath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    
print("Created FederatedLab, Evidence, Settings, and participant pages.")
