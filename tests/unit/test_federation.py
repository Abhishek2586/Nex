import numpy as np
import pytest
from nexora.federation.aggregate import fedavg


def test_weighted_fedavg_matches_independent_calculation():
    updates = [(1, {"x": np.array([1., 3.], dtype=np.float32)}),
               (2, {"x": np.array([2., 5.], dtype=np.float32)}),
               (3, {"x": np.array([4., 7.], dtype=np.float32)})]
    actual = fedavg(updates)["x"]
    np.testing.assert_allclose(actual, np.array([(1+4+12)/6, (3+10+21)/6], dtype=np.float32))


def test_fedavg_rejects_missing_shape_and_nonfinite():
    state = {"x": np.ones(2, dtype=np.float32)}
    with pytest.raises(ValueError):
        fedavg([(1, state), (1, state)])
    with pytest.raises(ValueError):
        fedavg([(1, state), (1, state), (1, {"x": np.ones(3, dtype=np.float32)})])
    with pytest.raises(ValueError):
        fedavg([(1, state), (1, state), (1, {"x": np.array([np.nan, 1], dtype=np.float32)})])
