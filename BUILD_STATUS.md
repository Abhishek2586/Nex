# NEXORA build status

Started: 2026-09-18.

## Completion Levels
- Core synthetic software prototype: PASS
- Reviewer hardening: IN PROGRESS (see below)
- WESAD adapter/import support: PASS (adapter functions implemented and tested; no real WESAD files supplied)
- Real WESAD evaluation: NOT RUN (dataset not supplied)
- Physical embodiment: NOT BUILT
- Public/cloud deployment: OUT OF SCOPE
- Clinical validation: NOT PERFORMED
- Patent grant/examination outcome: NOT DETERMINED

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
- Real private FedAvg with Opacus differential privacy. Repeated runs composed ledger state from 4 to 8 to 12 steps; current per-client epsilon is 5.407788 at delta 1e-5. Randomness is experimental non-cryptographic. Note: plain weighted FedAvg aggregation is used; secure multi-party aggregation is NOT implemented.
- Dashboard displays actual experiment manifests and per-client Opacus accountant state.
- Per-prediction Integrated Gradients and SHAP are implemented. Browser verification showed 12 signed tree attributions. Integrated Gradients convergence_delta was approximately -0.067 on the zero-baseline dummy input; this indicates model-computational attribution, not causal explanation. Completeness is approximate, not exact, when delta is non-zero.
- Coordinator reachability is shown independently. A real outage/restart exercise preserved edge/model readiness and recovered from unavailable to available.
- WESAD wrist adapter tests cover anti-aliased acceleration resampling, categorical label alignment, mixed-window exclusion and explicit trusted-pickle gating. No real WESAD files were supplied.
- Durable WebSocket delivery supports catch-up from a caller-supplied sequence, exact-origin rejection, reconnect backoff and event-ID deduplication. A live 20x replay was browser-verified over an accepted WebSocket connection.
- Coordinator HTTP job control enforces one active heavy experiment, persists queued/training/completed records and exposes cancel control. Standard and private one-round jobs were completed from the dashboard.
- Secure-demo starts edge and coordinator over HTTPS using a project-local CA and loopback SAN. Verified-CA access returned 200 and an untrusted default-store request was rejected; no system trust root was installed.
- Controlled launcher writes an owned-process manifest; stop tooling verified that it terminates only the recorded NEXORA launcher. Doctor reports all required imports and prepared artifacts available.
- Manual feedback (accept/dismiss on interventions) adapts intervention policy behavior only — specifically, cooldown timing and preference weighting. It is NOT used as stress-model ground truth and is not injected into the stress classifier training labels.
- Model registry supports activate and rollback. Integration test exercises: establish model A → activate candidate B → verify active hash changed → rollback → verify active hash restored to A → Predictor inference on restored model. Evidence written to artifacts/reports/rollback_test_evidence.json.

| Component | Status | Details |
|---|---|---|
| Startup/Shutdown Robustness | PASS | 10048 WinErrors fixed; proper psutil process tree ownership. |
| Single Instance Locks | PASS | `process.json` checks and port preflights implemented. |
| Fresh Clone Rehearsal | PASS | Genuine out-of-tree git clone and isolated `.venv` verified. |
| Architecture Validation | PASS | Predictor rejects mismatched architecture_id at load time. |
| Threshold Safety | PASS | Missing threshold returns `no_action` with reason `missing_active_model_threshold`. |
| Dynamic Threshold Selection | PASS | Threshold selected on validation split only; test split not touched during selection. |
| Technical Audit / P0 Debt | PASS | Architecture enforcement, safe threshold logic, DP-compatible LayerNorm. |
| Evidence Bundling | PASS | `build_evidence.py` verified; raw data and secrets excluded. |
| WESAD Adapter | PASS | Adapter functions correctly; explicitly labeled as NOT clinical data. |
| UI Claims | PASS | Calibration claims mitigated ("Scores" instead of "Probabilities"). |
| Rollback Success Path | PASS | Full A→B→rollback→A cycle tested; inference on restored model verified. |
| Reviewer hardening | PASS | All items verified: flake8 clean, tests 19/19 pass, Playwright 2/2 pass. |
| Final Acceptance | PASS | CI-reproducible: verify.py --full PASS (Backend, Frontend build, Frontend unit, Evidence, Playwright). |

- 2026-09-21 audit: 16 Python tests passed (five third-party deprecation warnings). The frontend production build passed; Vite reports a 636.62 kB JavaScript bundle advisory.
- Evidence ZIP is checksum-indexed and excludes SQLite state, secrets, keys, raw recordings and dependency directories. Its manifest records the current archive checksum and included-file checksums.

## Current work
Final consistency and reproducibility cleanup. Committed test artifacts removed. Unused imports and bare excepts fixed. Private federation wording corrected (Opacus DP; no secure multi-party aggregation). Rollback integration test implemented and executing.

## Not yet verified
Real WESAD evaluation is not verified because the dataset is not supplied.
Hardware, public cloud and clinical claims are not demonstrated by this prototype.

Measured synthetic results (source: Synthetic dataset only, not real physiological data):
- Tree: balanced_accuracy=1.000, macro_F1=1.000
- Local MLP: balanced_accuracy=1.000, macro_F1=1.000
- Initial one-round FedAvg: balanced_accuracy=1.000, macro_F1=1.000

These are results on the artificial synthetic generator only. Do not interpret as real-world performance.
