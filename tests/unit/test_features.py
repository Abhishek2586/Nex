import numpy as np
from nexora.data.synthetic import generate_subject
from nexora.features.extract import extract, normalize

def test_seed_and_feature_contract():
    a, _, _ = generate_subject(1)
    b, _, _ = generate_subject(1)
    np.testing.assert_array_equal(a, b)
    f = extract(a[:120])
    assert len(f["values"]) == 12
    assert np.isfinite(f["values"]).all()
    assert ((normalize(f["values"]) >= 0) & (normalize(f["values"]) <= 1)).all()

def test_missing_and_gap_repair():
    a, _, _ = generate_subject(1)
    a[10:14, 0] = np.nan
    assert extract(a[:120])["repaired"] == 4
    a[10:15, 0] = np.nan
    assert extract(a[:120])["values"] is None
    a[:, 0] = np.nan
    assert extract(a[:120])["reason"] == "insufficient_coverage"

def test_constant_signal_features():
    x = np.tile([2, 32, 0, 0, 1], (120, 1))
    f = extract(x)["values"]
    np.testing.assert_allclose(f, [2, 0, 0, 2, 32, 0, 0, 1, 0, 1, 0, 0], atol=1e-12)
