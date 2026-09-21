import os, subprocess, sys, time
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def run(name, cmd, cwd=root):
    print(f"[{name}] Starting...")
    res = subprocess.run(cmd, cwd=cwd, env=os.environ.copy())
    if res.returncode != 0:
        print(f"[{name}] Failed with exit code {res.returncode}")
        sys.exit(res.returncode)
    print(f"[{name}] Completed.")

def main():
    run("1. Install Backend Deps", [sys.executable, "-m", "pip", "install", "-e", ".[dev]"])
    run("2. Install Frontend Deps", ["npm.cmd", "install"], cwd=root/"frontend")
    run("3. Bootstrap", [sys.executable, "scripts/bootstrap.py"])
    run("4. Prepare Demo", [sys.executable, "scripts/prepare_demo.py"])
    run("5. Flake8", ["flake8", "src/nexora"])
    run("6. MyPy", ["mypy", "src/nexora", "--ignore-missing-imports"])
    run("7. Pytest", [sys.executable, "-m", "pytest", "tests/"])
    run("8. Frontend Build", ["npm.cmd", "run", "build"], cwd=root/"frontend")
    run("9. Frontend Unit Tests", ["npm.cmd", "run", "test"], cwd=root/"frontend")
    run("10. Playwright Install", ["npx.cmd", "playwright", "install", "--with-deps"], cwd=root/"frontend")

    print("[11. Start Services] Starting...")
    env = os.environ.copy()
    proc = subprocess.Popen([sys.executable, "scripts/start.py"], cwd=root, env=env)
    time.sleep(10) # wait for servers to bind
    
    try:
        env["BASE_URL"] = "http://127.0.0.1:8080"
        print("[12. Playwright E2E] Starting...")
        res = subprocess.run(["npx.cmd", "playwright", "test"], cwd=root/"frontend", env=env)
        if res.returncode != 0:
            print(f"[12. Playwright E2E] Failed")
            sys.exit(res.returncode)
        print("[12. Playwright E2E] Completed.")
        
        run("13. Build Evidence", [sys.executable, "scripts/build_evidence.py"])
    finally:
        run("14. Stop Services", [sys.executable, "scripts/stop.py"])
    
    print("Fresh clone verification complete. All operations succeeded.")

if __name__ == "__main__":
    main()
