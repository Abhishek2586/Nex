"""Train/evaluate CPU models on frozen participant-separated synthetic windows."""
import json, hashlib, time, platform
from pathlib import Path
import numpy as np
import torch
from torch import nn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, f1_score, confusion_matrix, classification_report
from safetensors.torch import save_file, load_file
from nexora.features.extract import normalize, SCHEMA_HASH, NAMES, LOW, HIGH

torch.set_num_threads(2)

ARCHITECTURE_ID = 'mlp-12-ln-32-16-2-v1'

def network():
    return nn.Sequential(nn.LayerNorm(12), nn.Linear(12,32),nn.ReLU(),nn.Linear(32,16),nn.ReLU(),nn.Linear(16,2))

def dataset(name='synthetic'):
    root = Path('data/synthetic') if name == 'synthetic' else Path('data/processed/wesad')
    manifest=json.loads((root/'manifest.json').read_text())
    with np.load(root/'windows.npz',allow_pickle=False) as d:
        return {k:d[k].copy() for k in d.files},manifest

def evaluate(y,p,threshold=0.5):
    pred=(np.asarray(p)[:, 1] > threshold).astype(int)
    return {'balanced_accuracy':float(balanced_accuracy_score(y,pred)), 'macro_f1':float(f1_score(y,pred,average='macro')), 'confusion_matrix':confusion_matrix(y,pred,labels=[0,1]).tolist(), 'classification_report':classification_report(y,pred,output_dict=True,zero_division=0), 'windows':len(y)}

def train(kind, dataset_name='synthetic', seed=42):
    d,m=dataset(dataset_name); x=d['x']; y=d['y']
    masks={k:np.isin(d['subjects'],v) for k,v in m['splits'].items()}
    started=time.time(); history=[]; model_dir=Path('models')/dataset_name/kind; model_dir.mkdir(parents=True,exist_ok=True)
    
    threshold_meta = {}
    
    if kind=='baseline':
        model=RandomForestClassifier(n_estimators=100,class_weight='balanced',random_state=seed,n_jobs=2)
        model.fit(x[masks['train']],y[masks['train']])
        # Safe numeric tree representation; no pickle model loading.
        arrays={}
        for i,tree in enumerate(model.estimators_):
            for key in ['children_left','children_right','feature','threshold','value']:
                arrays[f'{i}_{key}']=getattr(tree.tree_,key)
        np.savez_compressed(model_dir/'weights.npz',**arrays)
        p=model.predict_proba(x[masks['test']]); weight_path=model_dir/'weights.npz'
        metrics=evaluate(y[masks['test']],p,threshold=0.5)
    else:
        torch.manual_seed(seed); model=network(); optim=torch.optim.Adam(model.parameters(),lr=.001)
        tx=torch.tensor(normalize(x)); ty=torch.tensor(y,dtype=torch.long)
        best=float('inf'); stale=0; best_state=None
        generator=torch.Generator().manual_seed(seed)
        loader=torch.utils.data.DataLoader(torch.utils.data.TensorDataset(tx[masks['train']],ty[masks['train']]),batch_size=32,shuffle=True,generator=generator)
        for epoch in range(100):
            model.train()
            for bx,by in loader:
                optim.zero_grad(); loss=nn.functional.cross_entropy(model(bx),by); loss.backward(); optim.step()
            model.eval()
            with torch.no_grad(): val=float(nn.functional.cross_entropy(model(tx[masks['validation']]),ty[masks['validation']]))
            history.append({'epoch':epoch+1,'validation_loss':val})
            if val<best:
                best=val; stale=0; best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
            else: stale+=1
            if stale>=15: break
        model.load_state_dict(best_state); save_file(model.state_dict(),str(model_dir/'weights.safetensors'))
        weight_path=model_dir/'weights.safetensors'
        
        # Validation split threshold selection
        with torch.no_grad():
            val_p = model(tx[masks['validation']]).softmax(1).numpy()
        best_thresh = 0.5
        best_score = -1
        for t in np.linspace(0.1, 0.9, 81):
            t_pred = (val_p[:, 1] > t).astype(int)
            score = balanced_accuracy_score(y[masks['validation']], t_pred)
            if score > best_score:
                best_score = score
                best_thresh = float(t)
                
        threshold_meta = {
            'threshold': best_thresh,
            'threshold_selection_metric': 'balanced_accuracy',
            'validation_score': best_score,
            'selected_at': time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
            'architecture_id': ARCHITECTURE_ID
        }
        
        with torch.no_grad(): p=model(tx[masks['test']]).softmax(1).numpy()
        metrics=evaluate(y[masks['test']],p,threshold=best_thresh)
        
    majority=np.bincount(y[masks['train']]).argmax()
    metrics['majority_balanced_accuracy']=float(balanced_accuracy_score(y[masks['test']],np.full(masks['test'].sum(),majority)))
    
    # Safely get dataset hash if exists, otherwise empty
    dataset_hash = m.get('windows_sha256', '')
    
    report={'model_id':kind,'source':'Recorded dataset' if dataset_name == 'wesad' else 'Synthetic','task':'stress_vs_baseline','feature_schema_hash':SCHEMA_HASH,'feature_names':NAMES,'model_hash':hashlib.sha256(weight_path.read_bytes()).hexdigest(),'dataset_hash':dataset_hash,'splits':m['splits'],'metrics':metrics,'history':history,'duration_s':time.time()-started,'created_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'platform':platform.platform(),'python':platform.python_version()}
    report.update(threshold_meta)
    (model_dir/'metadata.json').write_text(json.dumps(report,indent=2))
    return report

class Predictor:
    def __init__(self, kind=None, dataset=None):
        registry_path = Path('models/registry/active.json')
        if kind is None and dataset is None and registry_path.is_file():
            active = json.loads(registry_path.read_text())
            self.kind = active['model_id']
            dataset = active['source']
            root = Path(active['artifact_path']) if 'artifact_path' in active else Path('models') / dataset / self.kind
            self.metadata = active
        else:
            self.kind = kind or 'neural'
            dataset = dataset or 'synthetic'
            root = Path('models') / dataset / self.kind
            if not (root / 'metadata.json').is_file():
                raise FileNotFoundError(f"No metadata found at {root}")
            self.metadata = json.loads((root / 'metadata.json').read_text())
            
        if self.metadata.get('feature_schema_hash') != SCHEMA_HASH: raise ValueError('Feature schema mismatch')
        
        path = root / ('weights.safetensors' if self.kind == 'neural' else 'weights.npz')
        if hashlib.sha256(path.read_bytes()).hexdigest() != self.metadata.get('model_hash'): raise ValueError('Model hash mismatch')
        
        if self.kind == 'neural':
            if self.metadata.get('architecture_id') != ARCHITECTURE_ID: raise ValueError(f"Architecture mismatch. Expected {ARCHITECTURE_ID}, got {self.metadata.get('architecture_id')}")
            self.model = network()
            self.model.load_state_dict(load_file(str(path)))
            self.model.eval()
        else:
            with np.load(path, allow_pickle=False) as d:
                self.trees = {k: d[k].copy() for k in d.files}
                
    def predict(self, values):
        x = np.atleast_2d(values)
        if self.kind == 'neural':
            with torch.no_grad(): return self.model(torch.tensor(normalize(x))).softmax(1).numpy()
        out = []
        for row in x:
            scores = []
            for i in range(100):
                t = lambda key: self.trees[f'{i}_{key}']; node = 0
                while t('children_left')[node] != -1:
                    node = int(t('children_left')[node] if row[int(t('feature')[node])] <= t('threshold')[node] else t('children_right')[node])
                counts = t('value')[node].reshape(-1); scores.append(counts / counts.sum())
            out.append(np.mean(scores, axis=0))
        return np.array(out)
        
    def explain(self, values):
        xraw = np.atleast_2d(values)
        target = int(self.predict(values)[0].argmax())
        if self.kind == 'neural':
            import torch, captum.attr
            tx = torch.tensor(normalize(xraw), requires_grad=True)
            ig = captum.attr.IntegratedGradients(self.model)
            baseline = torch.zeros_like(tx)
            attributions, delta = ig.attribute(tx, baseline, target=target, return_convergence_delta=True)
            return {'method': 'IntegratedGradients', 'output_space': 'probability', 'class': target, 'values': attributions[0].detach().tolist(), 'convergence_delta': float(delta[0]), 'feature_names': NAMES}
        else:
            import shap
            explainer = shap.PermutationExplainer(self.predict, np.zeros((1, 12)))
            shap_values = explainer(xraw)
            return {
                'method': 'SHAP PermutationExplainer', 
                'output_space': 'probability', 
                'class': target, 
                'values': shap_values.values[0, :, target].tolist(), 
                'completeness_delta': 0.0, 
                'feature_names': NAMES
            }
