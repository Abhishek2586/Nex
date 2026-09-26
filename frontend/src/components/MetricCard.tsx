import React from 'react';
export function MetricCard({ title, value, unit, status }: { title: string, value: any, unit?: string, status?: string }) {
  return <div className="card metric-card">
    <small>{title}</small>
    <strong>{value == null ? 'Unavailable' : Number(value).toFixed(2)} <em>{value == null ? '' : unit}</em></strong>
    {status && <span>{status}</span>}
  </div>;
}