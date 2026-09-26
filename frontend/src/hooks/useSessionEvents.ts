import { useState, useEffect } from 'react';
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
}