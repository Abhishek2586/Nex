import subprocess
import sys
import time
import urllib.request
import os

print("Starting backend...")
backend = subprocess.Popen([sys.executable, "scripts/start.py", "--port", "8000"], cwd=os.getcwd())

try:
    for _ in range(60):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health")
            break
        except Exception:
            time.sleep(0.5)
    else:
        print("Backend failed to start")
        sys.exit(1)

    print("Running frontend E2E tests...")
    res = subprocess.run(["npx", "playwright", "test"], cwd="frontend", shell=True)
    sys.exit(res.returncode)
finally:
    backend.terminate()
    backend.wait()
