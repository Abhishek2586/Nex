import React, { useState } from 'react';
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
            {health.wesad && health.wesad.recorded_evaluation_status === 'COMPLETED' && <option value="wesad">WESAD</option>}
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
                <thead><tr><th>Actual \ Pred</th><th>Baseline</th><th>Stress-like</th></tr></thead>
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
}