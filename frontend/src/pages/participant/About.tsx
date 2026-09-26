import React from 'react';
export function About() {
  return (
    <div className="card">
      <h2>About this prototype</h2>
      <p>NEXORA is a privacy-aware research prototype demonstrating edge-based machine learning for digital wellness interventions.</p>
      <p><b>Prototype Scope:</b></p>
      <ul>
        <li>Local software-only simulation.</li>
        <li>Uses synthetic or replayed data.</li>
        <li>Not a medical device.</li>
        <li>No clinical validation or claims.</li>
        <li>Future hardware embodiment (wrist-worn sensor) is simulated in this build.</li>
      </ul>
    </div>
  );
}