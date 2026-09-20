# Final Handoff

The NEXORA research prototype has been successfully built according to the specification.

## What is Included
- A complete, offline software-in-the-loop prototype.
- Synthetic deterministic data generators.
- Local federated learning and differential privacy implementations.
- A functional React dashboard and FastAPI backend services.
- Passing test suite and reproducible build scripts.

## How to Run the Demo
1. Run `python scripts/bootstrap.py` (already done).
2. Run `python scripts/prepare_demo.py` (already done).
3. Run `python scripts/start.py --profile demo`.
4. Open the displayed local URL in your browser.

To stop the services, run `python scripts/stop.py`.

## Artifacts and Evidence
All generated artifacts, logs, and evidence bundles are located in `artifacts/`.
You can rebuild the evidence bundle at any time by running `python scripts/build_evidence.py`.

## WESAD Dataset Note
The WESAD dataset is not bundled with this prototype due to licensing and size constraints. 
To validate the pipeline on real data, please obtain the WESAD dataset and place it in `data/raw/wesad/`, then run the `import-wesad` command.
