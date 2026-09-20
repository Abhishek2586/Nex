# Claim implementation map

| Claim | Status | Evidence and limit |
|---|---|---|
| 1(a) | simulated_input_or_output | `data/synthetic/manifest.json`; physical sensors absent. |
| 1(b) | partially_demonstrated | `src/nexora/edge/app.py`; local software processing, no embedded equivalence. |
| 1(c) | partially_demonstrated | local coordinator and jobs; no cloud hosting. |
| 1(d) | simulated_input_or_output | browser prompts; no physical actuation. |
| 2 | partially_demonstrated | Synthetic EDA, temperature and posture/motion; heart rate is a synthetic derived/demo channel and not a measured sensor. |
| 3 | implemented_software | narrow synthetic baseline/stress classifiers; no disease forecasting. |
| 4 | partially_demonstrated | persisted browser prompt and Manual feedback workflow; no haptics or efficacy evidence. |
| 5 | implemented_software | finite signed SHAP and Integrated Gradients values; LIME absent and attributions are not causal. |
| 6 | implemented_software | genuine three-process FedAvg on one host; no secure aggregation. |
| 7 | implemented_software | real Opacus example-level accounting on synthetic windows; no patient-level guarantee. |
| 8 | partially_demonstrated | reconnect, outage survival and verified loopback TLS; no physical IoT transport. |
| 9 | partially_demonstrated | WESAD adapter contract tested; no real wearable/hospital integration. |
| 10 | partially_demonstrated | end-to-end Synthetic software path; inherits physical limitations. |

These statuses describe implementation evidence and do not validate a patent claim or imply grant, novelty, clinical safety or efficacy.
