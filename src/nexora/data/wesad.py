"""Offline WESAD wrist-channel conversion into the NEXORA safe feature format.

Official WESAD pickle files are executable Python serialization. This module
loads them only after the operator explicitly marks the local source trusted.
Converted artifacts are NPZ/JSON and are subsequently loaded with
``allow_pickle=False``.
"""
import hashlib
import json
from pathlib import Path
import pickle
import numpy as np
from scipy.signal import resample_poly
from nexora.features.extract import extract, SCHEMA_HASH

EDA_HZ=4
TEMP_HZ=4
ACC_HZ=32
LABEL_HZ=700
LABEL_MAP={1:0,2:1}


def convert_arrays(eda,temp,acc,labels,subject_id):
    eda=np.asarray(eda,dtype=float).reshape(-1)
    temp=np.asarray(temp,dtype=float).reshape(-1)
    acc=np.asarray(acc,dtype=float)
    labels=np.asarray(labels).reshape(-1)
    if acc.ndim!=2 or acc.shape[1]!=3: raise ValueError('WESAD wrist ACC must have three axes')
    seconds=min(len(eda)/EDA_HZ,len(temp)/TEMP_HZ,len(acc)/ACC_HZ,len(labels)/LABEL_HZ)
    samples=int(seconds*EDA_HZ)
    if samples<120: raise ValueError('Subject has no complete 30-second window')
    eda=eda[:samples]; temp=temp[:samples]
    acceleration=resample_poly(acc[:int(seconds*ACC_HZ)],up=1,down=ACC_HZ//EDA_HZ,axis=0)[:samples]
    label_indices=np.minimum((np.arange(samples)*LABEL_HZ/EDA_HZ).astype(int),len(labels)-1)
    timeline_labels=np.array([LABEL_MAP.get(int(value),-1) for value in labels[label_indices]],dtype=np.int8)
    features=[]; targets=[]; starts=[]; excluded={}
    raw=np.column_stack([eda,temp,acceleration])
    for start in range(0,samples-119,120):
        window_labels=timeline_labels[start:start+120]
        unique=np.unique(window_labels)
        if len(unique)!=1 or unique[0] not in [0,1]:
            key='mixed_or_excluded'; excluded[key]=excluded.get(key,0)+1; continue
        result=extract(raw[start:start+120])
        if result['values'] is None:
            key=result['reason']; excluded[key]=excluded.get(key,0)+1; continue
        features.append(result['values']); targets.append(int(unique[0])); starts.append(start/EDA_HZ)
    return {'x':np.asarray(features,dtype=np.float64),'y':np.asarray(targets,dtype=np.int8),'starts_s':np.asarray(starts,dtype=np.float64),'subject':str(subject_id),'excluded_windows':excluded,'feature_schema_hash':SCHEMA_HASH}


def import_subject(path:Path,output_dir:Path,trusted_original=False):
    path=Path(path)
    if not trusted_original: raise ValueError('Refusing pickle load without --trusted-original confirmation')
    with path.open('rb') as handle:
        payload=pickle.load(handle,encoding='latin1')
    wrist=payload['signal']['wrist']
    subject=payload.get('subject',path.stem)
    result=convert_arrays(wrist['EDA'],wrist['TEMP'],wrist['ACC'],payload['label'],subject)
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    target=output_dir/f'{subject}.npz'
    np.savez_compressed(target,x=result['x'],y=result['y'],starts_s=result['starts_s'])
    metadata={key:value for key,value in result.items() if key not in ['x','y','starts_s']}
    metadata.update({'source':'Recorded dataset','source_dataset':'WESAD','input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'windows':len(result['y'])})
    target.with_suffix('.json').write_text(json.dumps(metadata,indent=2))
    return metadata


def import_directory(source:Path,output_dir=Path('data/processed/wesad'),trusted_original=False):
    source=Path(source)
    files=sorted(source.glob('S*/S*.pkl')) if source.is_dir() else [source]
    if not files: raise FileNotFoundError('No official-layout S*/S*.pkl files found')
    results=[import_subject(path,output_dir,trusted_original) for path in files]
    subjects = [item['subject'] for item in results]
    np.random.seed(42)
    shuffled = np.random.permutation(subjects).tolist()
    split_idx = int(len(shuffled) * 0.8)
    splits = {
        'train': shuffled[:split_idx],
        'test': shuffled[split_idx:]
    }
    
    # Also combine all npz into one windows.npz like synthetic data has
    all_x = []
    all_y = []
    all_starts = []
    all_subjects = []
    
    for res in results:
        data = np.load(output_dir / f"{res['subject']}.npz")
        all_x.append(data['x'])
        all_y.append(data['y'])
        all_starts.append(data['starts_s'])
        all_subjects.extend([res['subject']] * len(data['y']))
        
    if all_x:
        np.savez_compressed(
            output_dir / 'windows.npz',
            x=np.concatenate(all_x),
            y=np.concatenate(all_y),
            starts_s=np.concatenate(all_starts),
            subjects=np.array(all_subjects)
        )
        
    manifest={'real_dataset_status':'imported','source':'Recorded dataset','dataset':'WESAD','subjects':subjects,'subject_count':len(results),'splits':splits,'feature_schema_hash':SCHEMA_HASH}
    Path(output_dir).mkdir(parents=True,exist_ok=True)
    (Path(output_dir)/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest
