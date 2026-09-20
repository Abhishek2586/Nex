# Experiment protocol

The seeded Synthetic dataset contains 24 generated participants with ten minutes of 4 Hz signals each. The fixed participant split is 15 train, 3 validation and 6 test participants. Thirty-second windows do not cross participant or session boundaries. The task is synthetic baseline versus synthetic stress; model scores are uncalibrated.

The baseline is a random forest stored as numeric NPZ data. The neural model is an MLP stored with safetensors. Evaluation reads held-out test windows. Three fixed clients receive five training participants each. A federated round starts from the same MLP state, launches three separate worker processes, performs four local steps on 100 records per client, validates shape and round metadata, and aggregates by record count.

Private federation uses Opacus clipping and noise with max gradient norm 1.0, noise multiplier 1.2 and delta 1e-5. The privacy unit is one non-overlapping 30-second synthetic window. Ledgers persist by client and dataset identity so later executions compose. The latest prepared state is 12 optimizer steps and epsilon 5.407788 per client. Randomness is experimental and non-cryptographic; this is not patient-level privacy.

No real WESAD evaluation was run. The adapter requires an explicitly trusted original pickle, aligns labels, resamples wrist acceleration with anti-aliasing and excludes mixed-label windows.
