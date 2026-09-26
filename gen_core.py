import os
from pathlib import Path

root = Path("frontend/src")

files = {
    "types.ts": """export type Row = Record<string, any>;""",
    
    "api/client.ts": """export async function api(path: string, body?: unknown) {
  const r = await fetch('/api/v1/' + path, body === undefined ? {} : {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}""",

    "hooks/useNexoraData.ts": """import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Row } from '../types';

export function useNexoraData(selected: string) {
  const [health, H] = useState<Row>({});
  const [sessions, S] = useState<Row[]>([]);
  const [prompts, P] = useState<Row[]>([]);
  const [models, M] = useState<Row[]>([]);
  const [activeModel, AM] = useState<Row | null>(null);
  const [runs, R] = useState<Row[]>([]);
  const [jobs, J] = useState<Row[]>([]);
  const [privacy, V] = useState<Row[]>([]);
  const [projections, PROJ] = useState<Row[]>([]);
  const [error, ERR] = useState('');

  const refresh = async () => {
    try {
      const [h, s, p, m, am, r, v, proj, dstat] = await Promise.all([
        api('health'),
        api('sessions'),
        api('interventions'),
        api('models/catalog').catch(() => []),
        api('models/active').catch(() => null),
        api('experiments'),
        api('privacy'),
        api('privacy/projection'),
        api('data/status').catch(() => ({ wesad: { status: 'NOT RUN' } }))
      ]);
      h.wesad = dstat.wesad;
      H(h); S(s); P(p); M(m); AM(am); R(r); V(v); PROJ(proj);
      if (h.coordinator === 'available') {
        try { J(await api('experiment-jobs')); } catch { J([]); }
      } else J([]);
      ERR('');
    } catch (e) {
      ERR(String(e));
      H({ status: 'disconnected' });
    }
  };

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 2000);
    return () => clearInterval(timer);
  }, [selected]);

  return { health, sessions, prompts, models, activeModel, runs, jobs, privacy, projections, error, ERR, refresh, S };
}""",

    "hooks/useSessionEvents.ts": """import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Row } from '../types';

export function useSessionEvents(selected: string, ERR: (msg: string) => void) {
  const [events, E] = useState<Row[]>([]);
  
  useEffect(() => {
    E([]);
    if (!selected) return;
    let active = true, cursor = 0, socket: WebSocket | undefined, retry: number | undefined;
    
    const append = (rows: Row[]) => {
      if (active && rows.length) {
        cursor = rows[rows.length - 1].sequence;
        E(old => {
          const ids = new Set(old.map(item => item.event_id));
          return [...old, ...rows.filter(item => !ids.has(item.event_id))].slice(-1500);
        });
      }
    };
    
    const connect = async () => {
      try {
        append(await api(`sessions/${selected}/events?after=${cursor}&limit=1000`));
        const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        socket = new WebSocket(`${scheme}://${window.location.host}/api/v1/sessions/${selected}/stream?after=${cursor}`);
        socket.onmessage = e => append([JSON.parse(e.data)]);
        socket.onclose = () => { if (active) retry = window.setTimeout(connect, 750) };
        socket.onerror = () => socket?.close();
      } catch (e) {
        if (active) {
          ERR(String(e));
          retry = window.setTimeout(connect, 750);
        }
      }
    };
    
    connect();
    return () => {
      active = false;
      if (retry) clearTimeout(retry);
      socket?.close();
    };
  }, [selected]);
  
  return { events, E };
}""",

    "components/MetricCard.tsx": """import React from 'react';
export function MetricCard({ title, value, unit, status }: { title: string, value: any, unit?: string, status?: string }) {
  return <div className="card metric-card">
    <small>{title}</small>
    <strong>{value == null ? 'Unavailable' : Number(value).toFixed(2)} <em>{value == null ? '' : unit}</em></strong>
    {status && <span>{status}</span>}
  </div>;
}""",

    "app/routes.ts": """export const researchPages = ['Overview', 'System & Embodiment', 'Live session', 'Interventions', 'AI insights', 'Federated & privacy lab', 'Evidence', 'Settings'];
export const userPages = ['Home', 'Guidance', 'History', 'About', 'Settings'];
export const SCENARIOS: Record<string, string> = {
  'normal': 'Normal simulated session',
  'gradual_stress': 'Gradual stress-like change',
  'sustained_posture': 'Sustained posture deviation',
  'brief_posture': 'Brief posture deviation',
  'missing_data': 'Missing / low-quality signal',
  'high_motion': 'High-motion interference',
  'repeated_dismissal': 'Repeated prompt dismissal'
};"""
}

for filepath, content in files.items():
    p = root / filepath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    
print("Created base hooks, API, routes, and shared components.")
