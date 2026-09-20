# User guide

Run `\.venv\Scripts\python.exe scripts\doctor.py`, then `\.venv\Scripts\python.exe scripts\start.py --profile demo` and open `http://127.0.0.1:8080`. Overview starts, pauses, resumes and stops a labelled Synthetic replay. Live session shows streamed observations. Interventions records Manual feedback. AI insights explains actual stored model predictions. Federated & privacy lab launches local three-client jobs and shows persisted Opacus values. Evidence exposes claim status and the generated archive. Settings describes local source and demo constraints.

Use the sustained-posture scenario at 20× for a deterministic prompt. Use missing-data to observe inference abstention. A refresh restores persisted sessions and feedback. Run `\.venv\Scripts\python.exe scripts\stop.py` to stop only processes recorded by the launcher.

For WESAD, place files under a user-controlled directory and run `python -m nexora.cli data import-wesad --path <directory> --trusted-original` only after independently trusting the pickle source. The flag is intentional because arbitrary pickle loading is unsafe. Imported output is converted to safe numeric files. No WESAD data ships with the project.
