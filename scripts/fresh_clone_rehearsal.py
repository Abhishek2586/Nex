import os, subprocess, sys, time, json, datetime
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def get_npm():
    return 'npm.cmd' if sys.platform == 'win32' else 'npm'

def get_npx():
    return 'npx.cmd' if sys.platform == 'win32' else 'npx'

def run(name, cmd, cwd=root):
    print(f"[{name}] Starting...")
    res = subprocess.run(cmd, cwd=cwd, env=os.environ.copy())
    if res.returncode != 0:
        print(f"[{name}] Failed with exit code {res.returncode}")
        return False
    print(f"[{name}] Completed.")
    return True

def main():
    npm = get_npm()
    npx = get_npx()
    
    start_time = datetime.datetime.utcnow().isoformat() + 'Z'
    failed_stage = None
    
    import tempfile
    basetemp = tempfile.mkdtemp(prefix="nexora-pytest-")
    
    stages = [
        ("1. Install Backend Deps", [sys.executable, "-m", "pip", "install", "-e", ".[dev]"], root),
        ("2. Install Frontend Deps", [npm, "install"], root/"frontend"),
        ("3. Bootstrap", [sys.executable, "scripts/bootstrap.py"], root),
        ("4. Prepare Demo", [sys.executable, "scripts/prepare_demo.py"], root),
        ("5. Flake8", [sys.executable, "-m", "flake8", "src/nexora"], root),
        ("6. MyPy", [sys.executable, "-m", "mypy", "src/nexora", "--ignore-missing-imports"], root),
        ("7. Pytest", [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--basetemp={basetemp}", "tests/"], root),
        ("8. Frontend Build", [npm, "run", "build"], root/"frontend"),
        ("9. Frontend Unit Tests", [npm, "run", "test"], root/"frontend"),
        ("10. Playwright Install", [npx, "playwright", "install", "--with-deps"], root/"frontend"),
        ("11. Playwright E2E", [sys.executable, "scripts/test_e2e.py"], root),
        ("12. Build Evidence", [sys.executable, "scripts/build_evidence.py"], root)
    ]
    
    for name, cmd, cwd in stages:
        if not run(name, cmd, cwd):
            failed_stage = name
            break
            
    end_time = datetime.datetime.utcnow().isoformat() + 'Z'
    
    report = {
        "start_time": start_time,
        "end_time": end_time,
        "failed_stage": failed_stage,
        "success": failed_stage is None
    }
    
    report_path = root / 'artifacts/reports/clean-start.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    print(f"Wrote rehearsal report to {report_path}")
    
    if failed_stage:
        print(f"Rehearsal failed at stage: {failed_stage}")
        sys.exit(1)
        
    print("Fresh clone verification complete. All operations succeeded.")

if __name__ == "__main__":
    main()
