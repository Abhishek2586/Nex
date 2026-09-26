import React from 'react';
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
}