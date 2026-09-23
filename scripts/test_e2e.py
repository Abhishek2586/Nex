import subprocess
import sys
import time
import os
import json
import datetime
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def get_venv_python():
    """Return the project venv Python if it exists, otherwise sys.executable."""
    if sys.platform == 'win32':
        candidate = root / '.venv' / 'Scripts' / 'python.exe'
    else:
        candidate = root / '.venv' / 'bin' / 'python'
    return str(candidate) if candidate.exists() else sys.executable

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

    db_path = root / 'runtime/server.db'
    if db_path.exists():
        try:
            db_path.unlink()
            print("Cleared E2E database.")
        except Exception:
            pass

    coord_jobs_path = root / 'runtime/coordinator/jobs'
    if coord_jobs_path.exists():
        import shutil
        try:
            shutil.rmtree(coord_jobs_path)
            print("Cleared E2E coordinator jobs.")
        except Exception:
            pass

    print("Starting backend for E2E tests...")
    env = os.environ.copy()
    env['BASE_URL'] = f'http://127.0.0.1:{port}'
    
    # We use Popen, wait for it to be ready
    venv_python = get_venv_python()
    backend = subprocess.Popen([
        venv_python, "scripts/start.py",
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
    
    expected = 0
    unexpected = 0
    flaky = 0
    skipped = 0
    
    if json_report.exists():
        try:
            pw_res = json.loads(json_report.read_text())
            stats = pw_res.get('stats', {})
            expected = stats.get('expected', 0)
            unexpected = stats.get('unexpected', 0)
            flaky = stats.get('flaky', 0)
            skipped = stats.get('skipped', 0)
        except Exception:
            pass
            
    try:
        subprocess.run([venv_python, 'scripts/stop.py'], cwd=root, check=True)
        cleanup_result = "SUCCESS"
    except Exception as e:
        cleanup_result = f"FAIL: {e}"
        
    import socket
    ports_free = True
    for p in [port, port_b, port_c, coord_port]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', p)) == 0:
                ports_free = False
                cleanup_result = f"FAIL: Port {p} still occupied"
                break
                
    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    report = {
        "commit": get_git_commit(),
        "start_time": start_time,
        "end_time": end_time,
        "dashboard_url": f"http://127.0.0.1:{port}",
        "coordinator_url": f"http://127.0.0.1:{coord_port}",
        "owned_pids": pids,
        "playwright_exit_code": res.returncode,
        "expected": expected,
        "unexpected": unexpected,
        "flaky": flaky,
        "skipped": skipped,
        "ports_released": ports_free,
        "cleanup_result": cleanup_result
    }
    
    report_path = root / 'artifacts/reports/e2e-run.json'
    report_path.write_text(json.dumps(report, indent=2))
    print(f"Wrote E2E report to {report_path}")
    
    if unexpected > 0 or flaky > 0 or res.returncode != 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
