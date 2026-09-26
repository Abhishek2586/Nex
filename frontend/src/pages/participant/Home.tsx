import React from 'react';
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
}