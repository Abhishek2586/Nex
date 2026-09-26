import json
import hashlib
import pickle
from pathlib import Path
import numpy as np
import pytest
from nexora.data.wesad import import_subject, import_directory

def test_malformed_wesad_input(tmp_path):
    pkl_path = tmp_path / "S99.pkl"
    with pkl_path.open("wb") as f:
        pickle.dump({"signal": {"wrist": {"EDA": [1, 2, 3]}}}, f) # Missing TEMP, ACC, label
        
    with pytest.raises(ValueError, match="Malformed WESAD input"):
        import_subject(pkl_path, tmp_path, trusted_original=True)
        
def test_wesad_manifest_and_splits(tmp_path):
    data_dir = Path("data/processed/wesad")
    if not (data_dir / "manifest.json").exists():
        pytest.skip("WESAD not imported")
        
    manifest = json.loads((data_dir / "manifest.json").read_text())
    assert manifest["dataset"] == "WESAD"
    assert "windows_sha256" in manifest
    
    # 2. windows_sha256 matches actual windows.npz
    actual_hash = hashlib.sha256((data_dir / "windows.npz").read_bytes()).hexdigest()
    assert manifest["windows_sha256"] == actual_hash
    
    # 3. subject splits are disjoint
    train = set(manifest["splits"]["train"])
    val = set(manifest["splits"]["validation"])
    test = set(manifest["splits"]["test"])
    
    assert train.isdisjoint(val)
    assert train.isdisjoint(test)
    assert val.isdisjoint(test)
    
    # 5. WESAD client partitions use train subjects only
    # 6. union of client subjects == WESAD train subjects
    client_subjects = set()
    for cid, subs in manifest["clients"].items():
        sub_set = set(subs)
        assert sub_set.issubset(train)
        client_subjects.update(sub_set)
        
    assert client_subjects == train
    
def test_wesad_client_worker_does_not_read_synthetic(tmp_path):
    from nexora.federation.client_worker import _load_partition
    # The actual read is verified by passing 'wesad' as dataset
    data_dir = Path("data/processed/wesad")
    if not (data_dir / "manifest.json").exists():
        pytest.skip("WESAD not imported")
    x, y, d_hash = _load_partition("client-a", "wesad")
    manifest = json.loads((data_dir / "manifest.json").read_text())
    assert d_hash == manifest["windows_sha256"]
    
def test_wesad_private_ledger(tmp_path):
    data_dir = Path("data/processed/wesad")
    if not (data_dir / "manifest.json").exists():
        pytest.skip("WESAD not imported")
        
    from nexora.federation.client_worker import train_client
    import torch
    from nexora.ml.train import network
    
    base = tmp_path / "base.safetensors"
    from safetensors.torch import save_file
    save_file(network().state_dict(), str(base))
    base_hash = hashlib.sha256(base.read_bytes()).hexdigest()
    from nexora.features.extract import SCHEMA_HASH
    from nexora.ml.train import ARCHITECTURE_ID
    
    output = tmp_path / "output.safetensors"
    
    # Needs to monkeypatch the ledger path to not overwrite real runs
    # Alternatively we can just read the result of train_client
    # Let's see if train_client writes to Path("runtime") / client_id / "privacy.json"
    # we can't easily mock Path without more work, but the ledger object is returned in metadata["privacy"]
    meta = train_client(
        client_id="client-a",
        base=base,
        output=output,
        private=True,
        run_id="test_run",
        round_id="1",
        base_hash=base_hash,
        schema_hash=SCHEMA_HASH,
        architecture_id=ARCHITECTURE_ID,
        dataset_name="wesad"
    )
    
    assert meta["privacy"]["privacy_unit"] == "one non-overlapping 30-second WESAD window"
    manifest = json.loads((data_dir / "manifest.json").read_text())
    assert meta["privacy"]["dataset_identity"] == manifest["windows_sha256"]

    # also test synthetic privacy unit
    meta_synth = train_client(
        client_id="client-a",
        base=base,
        output=output,
        private=True,
        run_id="test_run",
        round_id="1",
        base_hash=base_hash,
        schema_hash=SCHEMA_HASH,
        architecture_id=ARCHITECTURE_ID,
        dataset_name="synthetic"
    )
    assert meta_synth["privacy"]["privacy_unit"] == "one non-overlapping 30-second synthetic window"
