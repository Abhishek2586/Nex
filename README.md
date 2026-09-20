# NEXORA — local research prototype

NEXORA is a software-in-the-loop research demonstrator. The completed core path uses explicitly labelled **Synthetic** signals; the optional WESAD adapter is implemented but no recorded WESAD data was supplied or evaluated. It is not medical software.

Prepare cached artifacts once:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_demo.py
```

Windows exam-day launch:

```powershell
.\.venv\Scripts\python.exe scripts\start.py --profile demo
```

Open http://127.0.0.1:8080. Stop the foreground server with Ctrl+C or run `.\.venv\Scripts\python.exe scripts\stop.py` from another terminal. Diagnose the prepared environment with `.\.venv\Scripts\python.exe scripts\doctor.py`.

The normal demo is offline and does not train at startup. Models use participant-separated splits. The tree's perfect synthetic score reflects the simple generator; neural utility is weak. Treat all probabilities as uncalibrated model scores, not medical conclusions. See [BUILD_STATUS.md](BUILD_STATUS.md), [ACCEPTANCE_REPORT.md](ACCEPTANCE_REPORT.md), and [docs/FINAL_HANDOFF.md](docs/FINAL_HANDOFF.md).
