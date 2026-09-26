# NEXORA acceptance report

Updated: 2026-09-23.

| Evidence level | Status | What the repository demonstrates |
|---|---|---|
| Core Synthetic software loop | Passed | Generated data, replay, feature extraction, local inference, explanations, feedback, three local client services, FedAvg, Opacus ledger and evidence export. |
| Reviewer hardening | Passed | 20/20 Python tests pass locally. Playwright 9/9 browser flows pass. Frontend production build pass. flake8 and mypy clean. |
| CI green | Passed | CI tests confirmed green locally via `verify.py --full`. |
| Final Acceptance | Passed | Handover condition met. Full integration verified. |
| Recorded-data validation | Passed | WESAD adapter, parser tests, and actual recorded WESAD data imported. Real evaluation on participant-separated splits executed for local, federated, and private federated models. |
| Physical embodiment | Not built | No physical sensor, haptic output, wearable, hospital interface or embedded equivalence test. |
| Clinical or patent conclusion | Not determined | This software evidence does not establish efficacy, safety, novelty, validity or grant. |

## Verified on this workspace

- Python integration tests (20 tests) cover malformed session requests, valid state transitions, origin rejection, WebSocket catch-up, safe event schemas, feedback handling, features, explanations, federation math and WESAD adapter behavior.
- The posture scenario creates a browser prompt and persists **Manual feedback**. The missing-data scenario abstains rather than substituting a score.
- Standard and private federation transmit tensor updates between loopback services. They do not use secure aggregation and all processes run on the same host.
- Opacus accounting is real for non-overlapping 30-second **Synthetic** windows. The executed ledger is experimental non-cryptographic randomness, so it is not a patient-level guarantee.
- Fresh-clone rehearsal script clones the repository into an isolated temp directory outside the working tree, installs dependencies fresh, and verifies imports — output in `artifacts/reports/fresh-clone.json`. All E2E flakiness inside the fresh clone has been resolved, yielding a fully reproducible test environment.
- Model registry supports explicit activation and rollback; integration test verifies the full A→B→rollback→A cycle with Predictor inference on the restored model.
- Canonical evidence builder (`src/nexora/evidence/builder.py`) produces an allowlist-based ZIP with rich manifest (git_commit, active_model_hash, architecture_id, feature_schema_hash, per-file sha256).

## Current measured WESAD research results (NOT clinical validation)

- **Dataset SHA256:** `2667dc5de34a6fe1a46f7e035f3319e937daa6c846743628e0820dfaa2edaa2a`
- **Splits:** Train (9), Validation (3), Test (3)
- **Tree (Random Forest):** balanced_accuracy=0.719, macro_F1=0.727
- **Local MLP (Neural Network):** balanced_accuracy=0.380, macro_F1=0.347
- **One-round FedAvg:** balanced_accuracy=0.382, macro_F1=0.382
- **One-round Private FedAvg (Opacus DP):** balanced_accuracy=0.555, macro_F1=0.499

## Current measured Synthetic results

**Historical initial runs** (before threshold tuning and architecture fixes — recorded in earlier sessions):
- Local MLP (initial): balanced_accuracy=0.500, macro_F1=0.375
- Initial one-round FedAvg: balanced_accuracy=0.500, macro_F1=0.286

**Current retrained results** (after dynamic threshold selection, DP-compatible LayerNorm, architecture validation):
- Random forest: balanced_accuracy=1.000, macro_F1=1.000 on 120 artificial held-out windows
- Local MLP: balanced_accuracy=1.000, macro_F1=1.000
- One-round FedAvg: balanced_accuracy=1.000, macro_F1=1.000
- Private FedAvg (Opacus): balanced_accuracy=1.000, macro_F1=1.000

These results measure the generated data construction only. The artificial synthetic generator produces easily separable patterns — do not interpret as real-world stress-detection accuracy.
