# NEXORA acceptance report

Updated: 2026-09-21.

| Evidence level | Status | What the repository demonstrates |
|---|---|---|
| Core Synthetic software loop | Passed | Generated data, replay, feature extraction, local inference, explanations, feedback, three local client services, FedAvg, Opacus ledger and evidence export. |
| Reviewer hardening | Partial | The UI, REST service separation, model activation and focused integration tests are implemented. The local Playwright suite passed on 2026-09-21; a clean-clone rehearsal and frontend component-unit tests remain open. |
| Recorded-data validation | Not verified | WESAD adapter and parser tests exist; no authorized WESAD subject data, model training or measured WESAD result is present. |
| Physical embodiment | Not built | No physical sensor, haptic output, wearable, hospital interface or embedded equivalence test. |
| Clinical or patent conclusion | Not determined | This software evidence does not establish efficacy, safety, novelty, validity or grant. |

## Verified on this workspace

- Python integration tests cover malformed session requests, valid state transitions, origin rejection, WebSocket catch-up, safe event schemas, feedback handling, features, explanations, federation math and WESAD adapter behavior.
- The posture scenario creates a browser prompt and persists **Manual feedback**. The missing-data scenario abstains rather than substituting a score.
- Standard and private federation transmit tensor updates between loopback services. They do not use secure aggregation and all processes run on the same host.
- Opacus accounting is real for non-overlapping 30-second **Synthetic** windows. The executed ledger is experimental non-cryptographic randomness, so it is not a patient-level guarantee.

## Current measured Synthetic results

Random forest: balanced accuracy 1.000, macro-F1 1.000 on 120 artificial held-out windows. Local MLP: 0.500 / 0.375. The recorded first non-private federated run: 0.500 / 0.286. The recorded private run: 0.500 / 0.375. These results measure the generated data construction only.
