import React from 'react';
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
}