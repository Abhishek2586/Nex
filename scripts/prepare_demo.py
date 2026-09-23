"""Prepare cached local demo artifacts without repeating matched private work."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + str(ROOT)

def main():
    print("Running phase A (Core Preparation)...")
    subprocess.run([sys.executable, "scripts/prepare_core.py"], cwd=ROOT, env=ENV, check=True)
    
    print("Starting temporary backend stack for federation...")
    backend_proc = subprocess.Popen([sys.executable, "scripts/start.py"], cwd=ROOT, env=ENV)
    
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
            raise RuntimeError("Temporary backend failed to start.")
            
        print("Running phase C (Federation Preparation)...")
        subprocess.run([sys.executable, "scripts/prepare_federation.py"], cwd=ROOT, env=ENV, check=True)
        
    finally:
        print("Stopping temporary backend stack...")
        subprocess.run([sys.executable, "scripts/stop.py"], cwd=ROOT, env=ENV)
        backend_proc.wait(timeout=10)
        
    print("Building evidence package...")
    subprocess.run([sys.executable, "scripts/build_evidence.py"], cwd=ROOT, env=ENV, check=True)
    
    print("Demo preparation complete.")

if __name__ == "__main__":
    main()
