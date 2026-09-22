"""Test that Predictor rejects models with wrong architecture_id."""
import hashlib
import json
import tempfile
import shutil
from pathlib import Path
import pytest

from nexora.ml.train import ARCHITECTURE_ID
from nexora.features.extract import SCHEMA_HASH


def test_architecture_id_mismatch_rejected():
    """Predictor must raise ValueError when metadata.architecture_id does not match
    the current ARCHITECTURE_ID constant."""
    tmp = Path(tempfile.mkdtemp(prefix='nexora-arch-test-'))
    try:
        model_dir = tmp / 'models' / 'synthetic' / 'neural'
        model_dir.mkdir(parents=True)

        # Write fake weights
        fake_weights = b'fake-weights'
        weights_path = model_dir / 'weights.safetensors'
        weights_path.write_bytes(fake_weights)
        model_hash = hashlib.sha256(fake_weights).hexdigest()

        meta = {
            'model_id': 'neural',
            'architecture_id': 'invalid-arch-that-does-not-match',
            'feature_schema_hash': SCHEMA_HASH,
            'model_hash': model_hash,
        }
        (model_dir / 'metadata.json').write_text(json.dumps(meta))

        # Patch Predictor to look in our temp dir
        import nexora.ml.train as train_mod
        original_path_cls = train_mod.Path

        class _PatchedPath(type(Path())):
            pass

        # Instead of patching Path globally (fragile), call Predictor directly
        # with kind+dataset so it uses the local models/ folder path.
        # We change cwd to tmp so relative 'models/' resolves into tmp.
        import os
        old_cwd = os.getcwd()
        os.chdir(tmp)
        try:
            from nexora.ml.train import Predictor
            with pytest.raises(ValueError, match="Architecture mismatch"):
                Predictor(kind='neural', dataset='synthetic')
        finally:
            os.chdir(old_cwd)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
