# NEXORA acceptance report

Updated: 2026-09-22.

| Evidence level | Status | What the repository demonstrates |
|---|---|---|
| Core Synthetic software loop | Passed | Generated data, replay, feature extraction, local inference, explanations, feedback, three local client services, FedAvg, Opacus ledger and evidence export. |
| Reviewer hardening | Passed | 19/19 Python tests pass locally and on GitHub Actions CI. Clean-clone rehearsal verified (`fresh-clone.json`). Playwright 2/2 browser flows pass. Frontend production build pass. flake8 and mypy clean. |
| CI green | Passed | GitHub Actions NEXORA CI is green on commit `f2053ef`. Tests are clean-clone safe and skip gracefully when generated model artifacts are absent. |
| Final Acceptance | Passed | verify.py --full PASS (2026-09-23): Backend 19/19, Frontend build, Frontend unit, Evidence build, Playwright 2/2. |
| Recorded-data validation | Not verified | WESAD adapter and parser tests exist; no authorized WESAD subject data, model training or measured WESAD result is present. |
| Physical embodiment | Not built | No physical sensor, haptic output, wearable, hospital interface or embedded equivalence test. |
| Clinical or patent conclusion | Not determined | This software evidence does not establish efficacy, safety, novelty, validity or grant. |

## Verified on this workspace

- Python integration tests (19 tests) cover malformed session requests, valid state transitions, origin rejection, WebSocket catch-up, safe event schemas, feedback handling, features, explanations, federation math and WESAD adapter behavior.
- The posture scenario creates a browser prompt and persists **Manual feedback**. The missing-data scenario abstains rather than substituting a score.
- Standard and private federation transmit tensor updates between loopback services. They do not use secure aggregation and all processes run on the same host.
- Opacus accounting is real for non-overlapping 30-second **Synthetic** windows. The executed ledger is experimental non-cryptographic randomness, so it is not a patient-level guarantee.
- Fresh-clone rehearsal script clones the repository into an isolated temp directory outside the working tree, installs dependencies fresh, and verifies imports — output in `artifacts/reports/fresh-clone.json`.
- Model registry supports explicit activation and rollback; integration test verifies the full A→B→rollback→A cycle with Predictor inference on the restored model.

## Current measured Synthetic results

Random forest: balanced accuracy 1.000, macro-F1 1.000 on 120 artificial held-out windows. Local MLP: 0.500 / 0.375. The recorded first non-private federated run: 0.500 / 0.286. The recorded private run: 0.500 / 0.375. These results measure the generated data construction only.
