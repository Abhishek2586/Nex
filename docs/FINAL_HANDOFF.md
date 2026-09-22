# Final handoff

Project: `D:\Downloads\Nexora`.

Prepare once with `\.venv\Scripts\python.exe scripts\prepare_demo.py`. Start the offline local demo with `\.venv\Scripts\python.exe scripts\start.py --profile demo`, then open `http://127.0.0.1:8080`. Stop only the owned launcher and client services with `\.venv\Scripts\python.exe scripts\stop.py`.

The working path is explicitly **Synthetic**: participant-separated generated data, a random forest and MLP, local replay, FastAPI/SQLite persistence, explanations, three loopback training services, sample-weighted FedAvg, Opacus accounting and a React dashboard. User interaction is labelled **Manual feedback**. The edge continues cached inference while the coordinator is unavailable.

Run `\.venv\Scripts\python.exe scripts\verify.py` for the backend suite, frontend production build and evidence rebuild. The report and demo instructions are in `artifacts/reports/PERFORMANCE.md` and `docs/DEMO_SCRIPT.md`; the export is `artifacts/reports/nexora-evidence.zip`.

WESAD is an optional **Recorded dataset** path. Its importer is present but no WESAD files, model run or recorded-data metric is included. Hardware, embedded deployment, secure aggregation, public cloud deployment, clinical validation and patent/legal conclusions remain outside what this project demonstrates.
