import React from 'react';
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
        <div className="card" data-testid="recent-predictions">
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
}