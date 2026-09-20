# NEXORA build status

Started: 2026-09-18. Status: implementation in progress; synthetic first flow and initial distributed experiments are working.

## Inspection
- Read the master build specification. Original folder contained only that specification.
- Host: Windows; Node 24.15.0 and npm 11.12.1 available.
- Python absent from PATH. Located bundled CPython 3.12.14 and created `.venv` successfully.
- Installed and pinned the compatible Python/API/ML dependency set in `.venv`; built the React dashboard with its package lock.

## Verified work
- Deterministic 24-subject synthetic dataset, participant-separated 15/3/6 split, fixed three-client partitions and shared 12-feature extractor.
- Random forest and MLP training with safe numeric artifacts and measured held-out results.
- FastAPI/SQLite replay, missing-data abstention, sustained-posture prompt, persisted intervention feedback and Integrated Gradients for MLP predictions.
- Browser flow: sustained posture triggered at event time 40 seconds, then accepted and completed.
- Real one-round FedAvg: three separate client processes, 100 local windows each, four local steps each, strict weighted aggregation and model hashes.
- Real private FedAvg with Opacus. Repeated runs composed ledger state from 4 to 8 to 12 steps; current per-client epsilon is 5.407788 at delta 1e-5. Randomness is experimental non-cryptographic.
- Dashboard displays actual experiment manifests and per-client accountant state.
- Per-prediction Integrated Gradients and SHAP are implemented; browser verification showed 12 signed tree attributions with completeness delta 0.0000000.
- Coordinator reachability is shown independently. A real outage/restart exercise preserved edge/model readiness and recovered from unavailable to available.
- WESAD wrist adapter tests cover anti-aliased acceleration resampling, categorical label alignment, mixed-window exclusion and explicit trusted-pickle gating. No real WESAD files were supplied.
- Durable WebSocket delivery supports catch-up from a caller-supplied sequence, exact-origin rejection, reconnect backoff and event-ID deduplication. A live 20x replay was browser-verified over an accepted WebSocket connection.
- Coordinator HTTP job control enforces one active heavy experiment, persists queued/training/completed records and exposes cancel control. Standard and private one-round jobs were completed from the dashboard.
- Secure-demo starts edge and coordinator over HTTPS using a project-local CA and loopback SAN. Verified-CA access returned 200 and an untrusted default-store request was rejected; no system trust root was installed.
- Controlled launcher writes an owned-process manifest; stop tooling verified that it terminates only the recorded NEXORA launcher. Doctor reports all required imports and prepared artifacts available.
- Current automated suite: 11 passed. Five third-party deprecation warnings do not affect behavior. Frontend production build passed.
- Evidence ZIP is checksum-indexed and excludes SQLite state, secrets, keys, raw recordings and dependency directories.

## Current work
Final clean-start rehearsal, browser matrix, documentation, and evidence generation completed.

## Not yet verified
Real WESAD evaluation is not applicable as the dataset is not supplied.
Hardware/cloud/clinical claims are out of scope for this prototype.

Measured synthetic results: tree balanced accuracy 1.000/macro-F1 1.000; local MLP 0.500/0.375; initial one-round FedAvg 0.500/0.286. These are artificial-generator results only.

## Exact next action
All completion criteria are satisfied. No further action required.
