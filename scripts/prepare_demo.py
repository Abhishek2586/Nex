"""Prepare cached local demo artifacts without repeating matched work.

Task 29: Ownership tracking — only stop the backend stack if THIS invocation started it.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + str(ROOT)


def _stack_is_already_running() -> bool:
    """Check if an existing owned NEXORA process manifest exists."""
    manifest_path = ROOT / 'runtime/control/process.json'
    if not manifest_path.exists():
        return False
    try:
        data = json.loads(manifest_path.read_text())
        return bool(data.get('pid'))
    except Exception:
        return False


def main():
    print("Running phase A (Core Preparation)...")
    subprocess.run([sys.executable, "scripts/prepare_core.py"], cwd=ROOT, env=ENV, check=True)

    # Task 29: Track ownership before starting the stack
    stack_already_running = _stack_is_already_running()
    backend_proc = None

    if stack_already_running:
        print("Existing NEXORA stack detected — reusing it (will NOT stop it on exit).")
        stack_started_by_this_process = False
    else:
        print("Starting temporary backend stack for federation...")
        backend_proc = subprocess.Popen([sys.executable, "scripts/start.py"], cwd=ROOT, env=ENV)
        stack_started_by_this_process = True

    try:
        # Wait for health checks
        manifest_path = ROOT / 'runtime/control/process.json'
        ready = False
        for _ in range(120):
            if manifest_path.exists():
                try:
                    if json.loads(manifest_path.read_text()).get('pid'):
                        ready = True
                        break
                except Exception:
                    pass
            time.sleep(1)

        if not ready:
            raise RuntimeError("Backend stack failed to become ready.")

        print("Running phase C (Federation Preparation)...")
        subprocess.run([sys.executable, "scripts/prepare_federation.py"], cwd=ROOT, env=ENV, check=True)

    finally:
        # Task 29: Only stop if we started it
        if stack_started_by_this_process:
            print("Stopping temporary backend stack (started by this process)...")
            subprocess.run([sys.executable, "scripts/stop.py"], cwd=ROOT, env=ENV)
            if backend_proc is not None:
                try:
                    backend_proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    backend_proc.kill()
        else:
            print("Leaving existing backend stack running (not owned by this process).")

    print("Building evidence package...")
    subprocess.run([sys.executable, "scripts/build_evidence.py"], cwd=ROOT, env=ENV, check=True)

    print("Demo preparation complete.")


if __name__ == "__main__":
    main()
