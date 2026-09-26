import React from 'react';

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
}