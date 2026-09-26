import React from 'react';
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
        <h3>Synthetic Data</h3>
        <button disabled={fedDisabled} onClick={() => act(() => api('experiment-jobs', { mode: 'federated', rounds: 1, dataset: 'synthetic' }))}>Run 1-round FedAvg</button>
        <button disabled={fedDisabled} onClick={() => act(() => api('experiment-jobs', { mode: 'federated', rounds: 3, dataset: 'synthetic' }))}>Run 3-round FedAvg</button>
        <button disabled={fedDisabled} onClick={() => act(() => api('experiment-jobs', { mode: 'federated', rounds: 5, dataset: 'synthetic' }))}>Run 5-round FedAvg</button>
        <button disabled={fedDisabled} onClick={() => act(() => api('experiment-jobs', { mode: 'private-federated', rounds: 1, dataset: 'synthetic' }))}>Run Private FedAvg (DP)</button>
        <span className={`badge ${health.coordinator === 'available' ? 'badge-success' : 'badge-error'}`}>Coordinator {health.coordinator}</span>
        {fedDisabled && <span className="muted" style={{ marginLeft: '0.5rem' }}>{fedReason}</span>}
        
        <h3 style={{ marginTop: '1rem' }}>WESAD Recorded Data</h3>
        <p><strong>WESAD measured experiment:</strong> {health.wesad?.recorded_evaluation_status === 'COMPLETED' ? 'Available' : 'Unavailable'}</p>
        <p><strong>Run new WESAD experiment:</strong> {health.wesad?.raw_data_available_locally ? 'Available' : 'Unavailable — raw WESAD dataset not present locally'}</p>
        
        <button disabled={fedDisabled || !health.wesad?.raw_data_available_locally} onClick={() => act(() => api('experiment-jobs', { mode: 'federated', rounds: 1, dataset: 'wesad' }))}>Run 1-round FedAvg (WESAD)</button>
        <button disabled={fedDisabled || !health.wesad?.raw_data_available_locally} onClick={() => act(() => api('experiment-jobs', { mode: 'private-federated', rounds: 1, dataset: 'wesad' }))}>Run Private FedAvg (WESAD)</button>
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
}