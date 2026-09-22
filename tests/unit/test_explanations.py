import pytest
import numpy as np
from pathlib import Path
from nexora.ml.train import Predictor


def test_tree_shap_is_signed_finite_and_complete():
    if not Path('models/synthetic/baseline/metadata.json').exists():
        pytest.skip('Baseline model not trained')
    with np.load('data/synthetic/windows.npz',allow_pickle=False) as data:
        features=data['x'][0]
    explanation=Predictor('baseline').explain(features)
    assert explanation['method']=='SHAP PermutationExplainer'
    assert len(explanation['values'])==12
    assert np.isfinite(explanation['values']).all()
    assert abs(explanation['completeness_delta'])<1e-6
