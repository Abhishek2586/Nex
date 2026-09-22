import os
import subprocess
import sys
import json
import datetime
import tempfile
import shutil
import platform
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def get_npm():
    return 'npm.cmd' if sys.platform == 'win32' else 'npm'

def get_npx():
    return 'npx.cmd' if sys.platform == 'win32' else 'npx'

def run(name, cmd, cwd):
    print(f"[{name}] Starting: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=cwd, env=os.environ.copy())
    if res.returncode != 0:
        print(f"[{name}] Failed with exit code {res.returncode}")
        return False, res.returncode
    print(f"[{name}] Completed.")
    return True, 0

def get_git_info(cwd):
    try:
        remote = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], cwd=cwd).decode('utf-8').strip()
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd).decode('utf-8').strip()
        return remote, sha
    except Exception as e:
        print(f"Failed to get git info: {e}")
        return "unknown", "unknown"

def main():
    npm = get_npm()
    npx = get_npx()
    
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    remote_url, head_sha = get_git_info(root)
    if remote_url == "unknown" or head_sha == "unknown":
        print("Must be run from inside a valid git repository with remote 'origin'.")
        sys.exit(1)
        
    temp_dir = tempfile.mkdtemp(prefix="nexora-rehearsal-")
    print(f"Created temporary clone directory: {temp_dir}")
    
    clone_dir = Path(temp_dir) / "Nexora"
    
    report = {
        "source_url": remote_url,
        "requested_sha": head_sha,
        "clone_path": str(clone_dir),
        "platform": platform.platform(),
        "python_version": sys.version,
        "commands": [],
        "success": False
    }

    try:
        # Step 4-5: Clone and checkout
        if not run("Git Clone", ["git", "clone", remote_url, str(clone_dir)], cwd=temp_dir)[0]:
            raise Exception("Failed to clone repository")
            
        if not run("Git Checkout", ["git", "checkout", head_sha], cwd=clone_dir)[0]:
            raise Exception(f"Failed to checkout {head_sha}")
            
        _, clone_sha = get_git_info(clone_dir)
        report["cloned_sha"] = clone_sha
        
        if clone_sha != head_sha:
            raise Exception(f"Clone HEAD ({clone_sha}) does not match source HEAD ({head_sha})")
            
        # Step 6: Verify no artifacts exist
        forbidden = [".venv", "data", "models", "runtime", "artifacts"]
        for f in forbidden:
            if (clone_dir / f).exists():
                raise Exception(f"Fresh clone contains forbidden file/dir: {f}")
                
        # Node versions
        try:
            node_v = subprocess.check_output(["node", "-v"]).decode('utf-8').strip()
            npm_v = subprocess.check_output([npm, "-v"]).decode('utf-8').strip()
            report["node_version"] = node_v
            report["npm_version"] = npm_v
        except:
            pass

        # Step 7: Create venv
        if not run("Create VENV", [sys.executable, "-m", "venv", ".venv"], cwd=clone_dir)[0]:
            raise Exception("Failed to create venv")
            
        # Step 8: Use clone python
        if sys.platform == 'win32':
            clone_python = str(clone_dir / ".venv" / "Scripts" / "python.exe")
        else:
            clone_python = str(clone_dir / ".venv" / "bin" / "python")
            
        basetemp = tempfile.mkdtemp(prefix="nexora-pytest-")

        # Step 9: Run stages
        stages = [
            ("Install Backend Deps", [clone_python, "-m", "pip", "install", "-e", ".[dev]"], clone_dir),
            ("Install Frontend Deps", [npm, "install"], clone_dir/"frontend"),
            ("Bootstrap", [clone_python, "scripts/bootstrap.py"], clone_dir),
            ("Prepare Demo", [clone_python, "scripts/prepare_demo.py"], clone_dir),
            ("Doctor", [clone_python, "scripts/doctor.py"], clone_dir),
            ("Pytest", [clone_python, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--basetemp={basetemp}", "tests/"], clone_dir),
            ("Frontend Build", [npm, "run", "build"], clone_dir/"frontend"),
            ("Frontend Unit Tests", [npm, "run", "test"], clone_dir/"frontend"),
            ("Playwright Install", [npx, "playwright", "install", "--with-deps"], clone_dir/"frontend"),
            ("Playwright E2E", [clone_python, "scripts/test_e2e.py"], clone_dir),
            ("Build Evidence", [clone_python, "scripts/build_evidence.py"], clone_dir)
        ]
        
        failed_stage = None
        for name, cmd, cwd in stages:
            if name == "Prepare Demo":
                print("[Start Backend] Launching in background...")
                backend_proc = subprocess.Popen([clone_python, "scripts/start.py"], cwd=clone_dir)
                import time
                manifest_path = clone_dir / 'runtime/control/process.json'
                ready = False
                for _ in range(180):
                    if manifest_path.exists():
                        try:
                            if json.loads(manifest_path.read_text()).get('pid'):
                                ready = True
                                break
                        except Exception:
                            pass
                    time.sleep(1)
                if not ready:
                    report["commands"].append({"name": "Start Backend", "exit_code": 1})
                    failed_stage = "Start Backend"
                    break
                report["commands"].append({"name": "Start Backend", "exit_code": 0})
                
            success, code = run(name, cmd, cwd)
            report["commands"].append({"name": name, "exit_code": code})
            if not success:
                failed_stage = name
                break
                
            if name == "Doctor":
                print("[Stop Backend] Shutting down background processes...")
                subprocess.run([clone_python, "scripts/stop.py"], cwd=clone_dir)
                
        # Parse test results from clone artifacts
        report["backend_tests_passed"] = None
        report["frontend_tests_passed"] = None
        report["playwright_expected"] = None
        report["playwright_unexpected"] = None
        report["playwright_flaky"] = None
        report["playwright_skipped"] = None
        report["cleanup_result"] = None
        
        e2e_json = clone_dir / 'artifacts' / 'reports' / 'e2e-run.json'
        if e2e_json.exists():
            try:
                e2e_data = json.loads(e2e_json.read_text())
                report["playwright_expected"] = e2e_data.get("expected", 0)
                report["playwright_unexpected"] = e2e_data.get("unexpected", 0)
                report["playwright_flaky"] = e2e_data.get("flaky", 0)
                report["playwright_skipped"] = e2e_data.get("skipped", 0)
                report["cleanup_result"] = e2e_data.get("cleanup_result")
            except:
                pass
                
        # Determine success
        if failed_stage is None and report["playwright_unexpected"] == 0 and report["playwright_flaky"] == 0:
            report["success"] = True

    except Exception as e:
        print(f"Rehearsal aborted: {e}")
        report["error"] = str(e)
    finally:
        # Step 10 & 11: Cleanup backend and processes
        if 'clone_dir' in locals() and clone_dir.exists():
            print("Ensuring backend processes are stopped...")
            subprocess.run([clone_python, "scripts/stop.py"], cwd=clone_dir)
            
        report["end_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Step 13: Write report to original repo
        report_path = root / 'artifacts' / 'reports' / 'fresh-clone.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2))
        print(f"Wrote rehearsal report to {report_path}")
        
        # Cleanup temp clone
        print(f"Cleaning up {temp_dir}...")
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: could not fully remove {temp_dir}: {e}")

    if not report["success"]:
        sys.exit(1)
        
    print("Fresh clone verification complete. All operations succeeded.")

if __name__ == "__main__":
    main()
