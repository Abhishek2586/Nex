# Troubleshooting

- If startup says prepared artifacts are missing, run `\.venv\Scripts\python.exe scripts\prepare_demo.py`.
- If port 8080 or 8100 is occupied, run `\.venv\Scripts\python.exe scripts\stop.py`; it only stops the recorded NEXORA process tree. Inspect unrelated listeners manually.
- If the coordinator badge is unavailable, local replay and cached inference continue. Run `\.venv\Scripts\python.exe scripts\restart_coordinator.py`.
- If the dashboard asset build is absent, run `npm.cmd ci` and `npm.cmd run build` from `frontend`. Exam-day startup never installs packages.
- A secure-demo certificate warning is expected in an ordinary browser because the project CA is deliberately not installed into system trust. Do not bypass the warning; use the scripted verified client check or explicitly install trust outside this project under your own policy.
- WESAD is optional. Missing files do not block Synthetic operation and must never be reported as recorded-data validation.
