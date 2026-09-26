# Final handoff

Project: `D:\Downloads\Nexora`.  
Last verified: 2026-09-22. GitHub Actions CI: green on commit `f2053ef`.

## Launch commands (Windows)

```
# Prepare once (idempotent — detects existing artifacts)
.venv\Scripts\python.exe scripts\prepare_demo.py

# Start the offline local demo
.venv\Scripts\python.exe scripts\start.py --profile demo

# Dashboard
http://127.0.0.1:8080

# Stop only the NEXORA-owned processes
.venv\Scripts\python.exe scripts\stop.py
```

## Exam-day 3-step checklist

1. **Open a terminal in `D:\Downloads\Nexora`.**  
   Run: `.venv\Scripts\python.exe scripts\doctor.py`  
   All items should say OK. If a model is missing, run `scripts\prepare_demo.py`.

2. **Start the stack:**  
   `.venv\Scripts\python.exe scripts\start.py --profile demo`  
   Wait for the dashboard URL to print, then open `http://127.0.0.1:8080`.

3. **After the demo, stop:**  
   `.venv\Scripts\python.exe scripts\stop.py`

**Recovery from a restart:** If the machine reboots mid-demo, re-run step 2. Sessions and experiment history are persisted in SQLite. No retraining is needed.

## What was implemented and executed

The working path is explicitly **Synthetic**: participant-separated generated data, a random forest and MLP, local replay, FastAPI/SQLite persistence, explanations, three loopback training services, sample-weighted FedAvg, Opacus accounting and a React dashboard. User interaction is labelled **Manual feedback**. The edge continues cached inference while the coordinator is unavailable.

Verified: 19 Python tests pass, frontend production build passes, flake8 and mypy clean, fresh-clone rehearsal passes (`artifacts/reports/fresh-clone.json`), Playwright 2/2 browser flows pass.

## Synthetic vs WESAD status

- **Synthetic:** All measured results and evidence. Fully functional.
- **WESAD (Recorded dataset):** Real WESAD recorded-data evaluation was executed locally. Raw WESAD source files are not distributed with the public repository.

## Evidence and report paths

| Artifact | Path |
|---|---|
| Technical report | `artifacts/reports/NEXORA_TECHNICAL_REPORT.md` |
| Performance record | `artifacts/reports/PERFORMANCE.md` |
| Evidence ZIP | `artifacts/reports/nexora-evidence.zip` |
| Demo script | `docs/DEMO_SCRIPT.md` |
| Claim map | `configs/claim_map.json` |
| Fresh-clone report | `artifacts/reports/fresh-clone.json` |
| Rollback evidence | `artifacts/reports/rollback_test_evidence.json` |
| Playwright report | `artifacts/reports/playwright-results.json` |

## Remaining limitations

- No physical sensors, wearable devices, haptics, embedded targets, hospital links, cloud deployment.
- No secure multi-party aggregation — FedAvg is plain sample-weighted averaging.
- Opacus ran in experimental non-cryptographic randomness mode (not deployment-grade DP).
- No patient-level privacy guarantee; privacy unit is one 30-second synthetic window.
- No formal decision-to-render p95 measurement.
- Inference/render latency not measured.
- Same-host process separation is not a security boundary.
- Patent legal status, grant outcome, and clinical conclusion are not determined by this prototype.
