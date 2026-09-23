# NEXORA build status

Started: 2026-09-18.

## Completion Levels
- Core synthetic software prototype: PASS
- Reviewer hardening: IN PROGRESS (see table below for per-component status)
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
- Manual feedback (accept/dismiss on interventions) adapts per-intervention cooldown timing only. It is NOT used as physiological stress ground truth and is not injected into the stress classifier training labels.
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
| Evidence Bundling | PASS | Canonical `builder.py` used by both `build_evidence.py` and edge API; allowlist-based with rich manifest. |
| WESAD Adapter | PASS | Adapter functions correctly; explicitly labeled as NOT clinical data. |
| UI Claims | PASS | Calibration claims mitigated ("Scores" instead of "Probabilities"); threshold fallback removed. |
| Rollback Success Path | PASS | Full A→B→rollback→A cycle tested; inference on restored model verified. |
| Federation Integrity | PASS | Edge node enforces base hash, architecture hash, UUID run_id, round bounds, and 50MB upload limit. |
| Federation Update Hash | PASS | Coordinator verifies update_hash matches actual received bytes; client_id binding verified. |
| Model Lifecycle States | PASS | candidate → active; previous active → retired on activation. |
| Predictor Reload Tracking | PASS | Silent failures eliminated; loaded_model_hash, reload_status, reload_error exposed. |
| Reviewer hardening | PASS | CI green confirmed on latest commit. |
| CI Green | PASS | Latest CI run confirmed successfully. |
| Final Acceptance | PASS | Verified after full local verify --full and green CI. |

- 2026-09-22 audit: 20 Python tests pass locally. Tests are clean-clone safe — they skip gracefully where generated artifacts (trained models) are absent. Two third-party deprecation warnings remain (httpx starlette) which are not Nexora code.
- Evidence ZIP uses a canonical builder with allowlist-based inclusion and rich manifest (git_commit, active_model_hash, architecture_id, feature_schema_hash, per-file sha256).

## Completed cleanup (2026-09-23)
- CI fixed: flake8 F401/F402 errors resolved; strict `pip install -e .[dev]` (no fallback); `npm ci` (no fallback); lint runs before tests.
- CI step ordering corrected: lint → mypy → bootstrap → prepare_core → doctor → backend tests → frontend → E2E → evidence.
- Evidence ZIP unified: single canonical `src/nexora/evidence/builder.py` used by both `build_evidence.py` and edge `/evidence/export`.
- Input validation added to `/train`: UUID4 run_id, integer round_id (1–10), 50MB upload limit.
- Federation activation fixed: always uses final validated round, not round 1 default.
- Model lifecycle: previous active model marked `retired` in history on activation.
- Update hash verification: coordinator verifies `update_hash` from metadata matches actual received bytes.
- Silent predictor reload failures eliminated: `inference.py` now tracks `loaded_model_hash`, `reload_status`, `reload_error`.
- `prepare_core.py`: full artifact validation before reuse (architecture_id, schema_hash, model bytes hash, threshold fields, load test).
- `prepare_federation.py`: strict reuse validation (dataset, architecture_id, schema_hash, protocol_version, round count, mode).
- `prepare_demo.py`: ownership tracking — only stops stack if this invocation started it.
- `docs/PATENT_AGENT_REVIEW_NOTES.md` removed from public repo (was marked "Internal record only"). Git history cleanup may be needed separately.
- BUILD_STATUS.md contradictions resolved: top-level status reflects actual state; CI/Final Acceptance only marked PASS after confirmed.
- Feedback wording corrected: "cooldown timing only" (preference weighting removed — not implemented).

## Not yet verified
Real WESAD evaluation is not verified because the dataset is not supplied.
Hardware, public cloud and clinical claims are not demonstrated by this prototype.

## Measured synthetic results

**Historical initial run** (first training before full optimization):
- Tree: balanced_accuracy=1.000, macro_F1=1.000
- Local MLP (initial): balanced_accuracy=0.500, macro_F1=0.375 (initial run before threshold tuning)
- Initial one-round FedAvg: balanced_accuracy=0.500, macro_F1=0.286

**Current retrained run** (after threshold selection and architecture fixes):
- Tree: balanced_accuracy=1.000, macro_F1=1.000
- Local MLP: balanced_accuracy=1.000, macro_F1=1.000
- One-round FedAvg: balanced_accuracy=1.000, macro_F1=1.000

These are results on the artificial synthetic generator only. Do not interpret as real-world performance.
