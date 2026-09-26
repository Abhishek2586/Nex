import os
from pathlib import Path

root = Path("frontend/src")

files = {
    "app/App.tsx": """import React, { useState } from 'react';
import { BrowserRouter, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useNexoraData } from '../hooks/useNexoraData';
import { useSessionEvents } from '../hooks/useSessionEvents';
import { researchPages, userPages, SCENARIOS } from './routes';

import { Overview } from '../pages/research/Overview';
import { LiveSession } from '../pages/research/LiveSession';
import { Interventions } from '../pages/research/Interventions';
import { AIInsights } from '../pages/research/AIInsights';
import { FederatedLab } from '../pages/research/FederatedLab';
import { Evidence } from '../pages/research/Evidence';
import { SystemEmbodiment } from '../pages/research/SystemEmbodiment';

import { Home } from '../pages/participant/Home';
import { Guidance } from '../pages/participant/Guidance';
import { History } from '../pages/participant/History';
import { About } from '../pages/participant/About';
import { Settings } from '../pages/Settings';

export function App() {
  const [selected, SEL] = useState('');
  const [scenario, SC] = useState('normal');
  const [speed, SP] = useState(20);
  const [mode, setMode] = useState(() => localStorage.getItem('nexora-view') || 'research');
  
  const { health, sessions, prompts, models, activeModel, runs, jobs, privacy, error, catalog, ERR, refresh, S } = useNexoraData(selected);
  const { events, E } = useSessionEvents(selected, ERR);

  const navigate = useNavigate();
  const routerLocation = useLocation();
  const pageRaw = decodeURIComponent(routerLocation.pathname.slice(1));
  const page = pageRaw ? pageRaw : mode === 'research' ? 'Overview' : 'Home';
  
  const activePages = mode === 'research' ? researchPages : userPages;
  const setAppMode = (next: string) => {
    setMode(next);
    localStorage.setItem('nexora-view', next);
    navigate(next === 'research' ? '/Overview' : '/Home');
  };

  const act = async (fn: () => Promise<unknown>) => {
    try {
      await fn();
      await refresh();
    } catch (e) {
      ERR(String(e));
    }
  };

  const start = () => act(async () => {
    const s = await api('sessions', { scenario, speed, seed: 42 });
    await api(`sessions/${s.id}/start`, {});
    SEL(s.id);
  });
  
  // ensure selection is valid if sessions load
  if (sessions.length && !selected) SEL(sessions[0].id);

  const session = sessions.find(s => s.id === selected);
  const obs = events.filter((e:any) => e.event_type === 'observation').map((e:any) => {
    const o = { ...e.payload, ...e.payload.signals };
    o.acc_mag_g = (o.acc_x_g != null && o.acc_y_g != null && o.acc_z_g != null) ? Math.sqrt(o.acc_x_g ** 2 + o.acc_y_g ** 2 + o.acc_z_g ** 2) : null;
    return o;
  });
  const latest = obs.at(-1);
  const pred = events.filter((e:any) => e.event_type === 'prediction').at(-1)?.payload;
  const activePrompts = prompts.filter((p:any) => (p.status === 'offered' || p.status === 'accepted') && (p.session_id === selected));
  const fedDisabled = health.coordinator !== 'available' || jobs.some((j:any) => ['queued', 'training'].includes(j.status));
  const fedReason = health.coordinator !== 'available' ? 'Coordinator unavailable' : (jobs.some((j:any) => ['queued', 'training'].includes(j.status)) ? 'Experiment already running' : '');

  return (
    <div className="shell">
      <aside>
        <div className="brand"><b>◈ NEXORA</b><small>{mode === 'research' ? 'RESEARCH CONSOLE' : 'PARTICIPANT APP'}</small></div>
        <div className="mode-toggle" style={{ padding: '0 1rem', marginBottom: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff', fontSize: '0.875rem' }}>
            <input aria-label="Research Mode" type="checkbox" checked={mode === 'research'} onChange={(e) => setAppMode(e.target.checked ? 'research' : 'user')} />
            Research Mode
          </label>
        </div>
        <nav>
          {activePages.map((p, i) => (
            <NavLink key={p} to={'/' + p}>
              <span>{['▦', '⌁', '◎', '◇', '⬡', '▤', '⚙', '★'][i % 8]}</span><span>{p}</span>
            </NavLink>
          ))}
        </nav>
        <div className="asidebottom"><span className="dot" /> Local workspace<small>Software-in-the-loop prototype</small></div>
      </aside>
      <main>
        <header>
          <span>Workspace / <b>{page}</b></span>
          <div className="badges">
            <span className="badge">Synthetic</span>
            <span className="badge">{health.client_id || 'client-a'}</span>
            <span className="badge">Edge {health.status || 'Connecting…'}</span>
            <span className="badge">Coordinator {health.coordinator || 'unknown'}</span>
          </div>
        </header>
        <section>
          <div className="title">
            <div>
              <p className="eyebrow">NEXORA / {mode === 'research' ? 'RESEARCH WORKSPACE' : 'PARTICIPANT DASHBOARD'}</p>
              <h1>{page}</h1>
              <p>{mode === 'research' ? 'Inspect signals, model behaviour and traceable software decisions.' : 'Follow the local simulation and choose whether to use an optional suggestion.'}</p>
            </div>
            <span className="badge">{health.transport || 'Connecting…'}</span>
          </div>
          {error && <div role="alert" className="error">{error}</div>}

          {page === 'Overview' && mode === 'research' && <Overview {...{ mode, scenario, speed, setScenario: SC, setSpeed: SP, start, session, selected, refresh, events, activeModel, activePrompts, latest, pred, SCENARIOS }} />}
          {page === 'Live session' && mode === 'research' && <LiveSession {...{ selected, scenario, session, speed, activeModel, pred, activePrompts, latest, obs, events }} />}
          {page === 'Interventions' && mode === 'research' && <Interventions {...{ prompts, act }} />}
          {page === 'AI insights' && mode === 'research' && <AIInsights {...{ health, models: catalog, pred, act, refresh }} />}
          {page === 'Federated & privacy lab' && mode === 'research' && <FederatedLab {...{ health, jobs, privacy, runs, fedDisabled, fedReason, act }} />}
          {page === 'Evidence' && mode === 'research' && <Evidence {...{ health, models: catalog, activeModel }} />}
          {page === 'System & Embodiment' && mode === 'research' && <SystemEmbodiment />}
          
          {page === 'Home' && mode === 'user' && <Home {...{ session, pred, activePrompts, latest, start, act, selected }} />}
          {page === 'Guidance' && mode === 'user' && <Guidance {...{ activePrompts, act }} />}
          {page === 'History' && mode === 'user' && <History {...{ sessions, selected, events, SEL }} />}
          {page === 'About' && mode === 'user' && <About />}
          {page === 'Settings' && <Settings {...{ speed, setSpeed, activeModel }} />}
        </section>
        <footer>Research prototype · Recorded/simulated inputs · No live health measurements.</footer>
      </main>
    </div>
  );
}""",

    "main.tsx": """import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { App } from './app/App';
import './style.css';

createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);"""
}

for filepath, content in files.items():
    p = root / filepath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    
print("Created App.tsx and main.tsx")
