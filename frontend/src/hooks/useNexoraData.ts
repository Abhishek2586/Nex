import { useState, useEffect } from 'react';
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
}