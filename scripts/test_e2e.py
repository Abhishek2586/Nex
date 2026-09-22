import subprocess
import sys
import time
import os
import json
import datetime
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def get_npx():
    return 'npx.cmd' if sys.platform == 'win32' else 'npx'
    
def get_git_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode('utf-8').strip()
    except Exception:
        return 'unknown'

def main():
    manifest = root / 'runtime/control/process.json'
    if manifest.exists():
        print("A NEXORA stack is already running or a stale manifest exists. Please stop it first.")
        sys.exit(1)

    start_time = datetime.datetime.utcnow().isoformat() + 'Z'
    port = 8090
    port_b = 8092
    port_c = 8093
    coord_port = 8190

    print("Starting backend for E2E tests...")
    env = os.environ.copy()
    env['BASE_URL'] = f'http://127.0.0.1:{port}'
    
    # We use Popen, wait for it to be ready
    backend = subprocess.Popen([
        sys.executable, "scripts/start.py",
        "--port", str(port),
        "--port-b", str(port_b),
        "--port-c", str(port_c),
        "--coordinator-port", str(coord_port)
    ], cwd=root)

    ready = False
    for _ in range(60):
        if manifest.exists():
            try:
                record = json.loads(manifest.read_text())
                if record.get('port') == port:
                    ready = True
                    break
            except Exception:
                pass
        time.sleep(1)

    if not ready:
        print("Backend failed to start properly.")
        if backend.poll() is None:
            backend.terminate()
        sys.exit(1)

    pids = [backend.pid]
    try:
        record = json.loads(manifest.read_text())
        pids.append(record.get('pid'))
        for child in record.get('children', []):
            pids.append(child.get('pid'))
    except Exception:
        pass
    pids = list(set(pids) - {None})

    print("Running frontend E2E tests...")
    npx = get_npx()
    
    json_report = root / 'artifacts/reports/playwright-results.json'
    json_report.parent.mkdir(parents=True, exist_ok=True)
    if json_report.exists():
        json_report.unlink()
        
    env['PLAYWRIGHT_JSON_OUTPUT_NAME'] = str(json_report.resolve())
    
    res = subprocess.run([npx, "playwright", "test", "--reporter=list,json"], cwd=root/"frontend", env=env)
    
    tests_passed = "unknown"
    tests_failed = "unknown"
    
    if json_report.exists():
        try:
            pw_res = json.loads(json_report.read_text())
            stats = pw_res.get('stats', {})
            tests_passed = stats.get('expected', 0)
            tests_failed = stats.get('unexpected', 0) + stats.get('flaky', 0)
        except Exception:
            pass
            
    try:
        subprocess.run([sys.executable, 'scripts/stop.py'], cwd=root, check=True)
        cleanup_result = "SUCCESS"
    except Exception as e:
        cleanup_result = f"FAIL: {e}"
        
    end_time = datetime.datetime.utcnow().isoformat() + 'Z'
    
    report = {
        "commit": get_git_commit(),
        "start_time": start_time,
        "end_time": end_time,
        "dashboard_url": f"http://127.0.0.1:{port}",
        "coordinator_url": f"http://127.0.0.1:{coord_port}",
        "owned_pids": pids,
        "playwright_exit_code": res.returncode,
        "tests_passed": tests_passed,
        "tests_failed": tests_failed,
        "cleanup_result": cleanup_result
    }
    
    report_path = root / 'artifacts/reports/e2e-run.json'
    report_path.write_text(json.dumps(report, indent=2))
    print(f"Wrote E2E report to {report_path}")
    
    sys.exit(res.returncode)

if __name__ == '__main__':
    main()
