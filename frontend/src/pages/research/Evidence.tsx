import React from 'react';

export function Evidence({ health, models, activeModel }: any) {
  const exportEvidence = () => { window.location.href = '/api/v1/evidence/export'; };

  return (
    <div className="card">
      <h2>Evidence package</h2>
      {health.wesad && (health.wesad.centralized_status === 'COMPLETED' || health.wesad.import_status === 'COMPLETED') ? (
        <div style={{ background: 'var(--surface)', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1rem' }}>
          <p><strong>WESAD offline evaluation:</strong> COMPLETED</p>
          <p><strong>Imported subjects:</strong> {health.wesad.subject_count}</p>
          <p><strong>Train / Val / Test split counts:</strong> {health.wesad.splits.train?.length} / {health.wesad.splits.validation?.length} / {health.wesad.splits.test?.length}</p>
          <p><strong>Dataset SHA256:</strong> {health.wesad.dataset_hash}</p>
          <p><strong>Baseline model hash:</strong> {models.find((m:any) => m.model_id === 'baseline' && m.source === 'Recorded dataset')?.model_hash?.slice(0, 8) || 'N/A'}</p>
          <p><strong>Neural model hash:</strong> {models.find((m:any) => m.model_id === 'neural' && m.source === 'Recorded dataset')?.model_hash?.slice(0, 8) || 'N/A'}</p>
          <p><strong>Measured test metrics (Baseline):</strong> Balanced Acc: {((models.find((m:any) => m.model_id === 'baseline' && m.source === 'Recorded dataset')?.test_balanced_accuracy || 0) * 100).toFixed(1)}% · Macro-F1: {(models.find((m:any) => m.model_id === 'baseline' && m.source === 'Recorded dataset')?.test_macro_f1 || 0).toFixed(3)}</p>
          <p><strong>Measured test metrics (Neural):</strong> Balanced Acc: {((models.find((m:any) => m.model_id === 'neural' && m.source === 'Recorded dataset')?.test_balanced_accuracy || 0) * 100).toFixed(1)}% · Macro-F1: {(models.find((m:any) => m.model_id === 'neural' && m.source === 'Recorded dataset')?.test_macro_f1 || 0).toFixed(3)}</p>
          <p><strong>Federated run status:</strong> {health.wesad.federated_status}</p>
          <p><strong>Private federated run status:</strong> {health.wesad.private_federated_status}</p>
        </div>
      ) : (
        <div style={{ background: 'var(--surface)', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1rem' }}>
          <p><strong>WESAD offline evaluation:</strong> NOT RUN</p>
        </div>
      )}
      <div style={{ background: 'var(--surface)', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1rem' }}>
        <p><strong>Active model:</strong> {activeModel ? activeModel.model_hash?.slice(0, 8) || 'None' : 'No active model'}</p>
        <p><strong>Architecture:</strong> {activeModel?.architecture_id || 'Unavailable'}</p>
        <p><strong>Threshold:</strong> {activeModel?.threshold != null ? activeModel.threshold : 'Unavailable'}</p>
        <p><strong>Lifecycle:</strong> {activeModel?.lifecycle_state || 'Unavailable'}</p>
        <p><strong>Source:</strong> Synthetic dataset (seeded, artificial)</p>
        <p><strong>Verification:</strong> Hash-indexed; see export-manifest.json inside ZIP</p>
      </div>
      <button onClick={exportEvidence} id="download-evidence-zip">Download ZIP Evidence</button>
    </div>
  );
}