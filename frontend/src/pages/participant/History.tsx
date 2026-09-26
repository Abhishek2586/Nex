import React from 'react';
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
}