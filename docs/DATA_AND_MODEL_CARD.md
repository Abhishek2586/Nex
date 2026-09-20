# Data and model card

The executed source is **Synthetic**: 24 deterministic subjects, ten minutes at 4 Hz, split by subject into 15 train, 3 validation and 6 test subjects. Each federated client receives five training subjects. Thirty-second non-overlapping windows produce the 12 features defined in the master specification.

Measured first-run held-out results:

| Model | Balanced accuracy | Macro-F1 | Test windows |
| --- | ---: | ---: | ---: |
| Random forest | 1.000 | 1.000 | 120 |
| Local MLP | 0.500 | 0.375 | 120 |
| One-round FedAvg MLP | 0.500 | 0.286 | 120 |
| One-round private FedAvg examples | 0.500 | 0.375 | 120 |

These numbers measure fit to the artificial generator only. The tree result indicates that this synthetic construction is easily separable. It does not establish physiological validity or clinical performance.

The WESAD adapter resamples wrist acceleration from 32 Hz to the 4 Hz EDA/temperature timeline with anti-alias filtering, aligns 700 Hz categorical labels without interpolation, retains baseline/stress only, rejects mixed windows, and saves safe NPZ/JSON output. Parser tests pass; real dataset status remains unavailable because no authorized subject files were supplied.
