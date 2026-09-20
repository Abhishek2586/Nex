import numpy as np
import pytest
from nexora.data.wesad import convert_arrays,import_subject


def test_wesad_resampling_labels_and_exclusions(tmp_path):
    seconds=90
    eda=np.linspace(1,2,seconds*4)
    temp=np.linspace(32,31.5,seconds*4)
    acc=np.zeros((seconds*32,3)); acc[:,2]=1
    labels=np.ones(seconds*700,dtype=int)
    labels[30*700:60*700]=2
    labels[60*700:]=3
    result=convert_arrays(eda,temp,acc,labels,'S-test')
    assert result['x'].shape==(2,12)
    assert result['y'].tolist()==[0,1]
    assert result['excluded_windows']=={'mixed_or_excluded':1}
    assert np.isfinite(result['x']).all()


def test_pickle_requires_explicit_trust(tmp_path):
    source=tmp_path/'S2.pkl'; source.write_bytes(b'not opened')
    with pytest.raises(ValueError,match='trusted-original'):
        import_subject(source,tmp_path/'out',trusted_original=False)
