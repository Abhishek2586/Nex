import argparse
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def get_npm():
    return 'npm.cmd' if sys.platform == 'win32' else 'npm'

def main():
    parser = argparse.ArgumentParser(description="NEXORA verification script")
    parser.add_argument('--full', action='store_true', help="Run full verification including E2E Playwright tests")
    args = parser.parse_args()

    environment = os.environ.copy()
    environment['PYTHONPATH'] = str(root / 'src') + os.pathsep + str(root)
    environment['MPLCONFIGDIR'] = str(root / 'runtime/matplotlib')

    npm = get_npm()

    import tempfile
    basetemp = tempfile.mkdtemp(prefix="nexora-pytest-")

    steps = [
        ('Backend tests', [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', f'--basetemp={basetemp}'], root),
        ('Frontend build', [npm, 'run', 'build'], root / 'frontend'),
        ('Frontend unit tests', [npm, 'run', 'test'], root / 'frontend'),
        ('Evidence build', [sys.executable, 'scripts/build_evidence.py'], root)
    ]

    results = {}
    
    for name, command, cwd in steps:
        print(f"Running: {name}...")
        try:
            completed = subprocess.run(command, cwd=cwd, env=environment)
            if completed.returncode == 0:
                results[name] = 'PASS'
            else:
                results[name] = 'FAIL'
                break
        except FileNotFoundError:
            results[name] = 'FAIL (command not found)'
            break
        except Exception as e:
            results[name] = f'FAIL ({e})'
            break
            
    if args.full and all(res == 'PASS' for res in results.values()):
        name = 'Playwright'
        print(f"Running: {name}...")
        completed = subprocess.run([sys.executable, 'scripts/test_e2e.py'], cwd=root, env=environment)
        if completed.returncode == 0:
            results[name] = 'PASS'
        else:
            results[name] = 'FAIL'

    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)
    
    print(f"Backend tests: {results.get('Backend tests', 'SKIPPED')}")
    print(f"Frontend build: {results.get('Frontend build', 'SKIPPED')}")
    print(f"Frontend unit tests: {results.get('Frontend unit tests', 'SKIPPED')}")
    print(f"Evidence build: {results.get('Evidence build', 'SKIPPED')}")
    
    if args.full:
        print(f"Playwright: {results.get('Playwright', 'SKIPPED')}")
    else:
        print("Playwright: NOT RUN")
                
    print("="*50)

    if any(res.startswith('FAIL') for res in results.values()):
        print("Verification FAILED.")
        sys.exit(1)
    else:
        print("NEXORA current verification passed.")
        sys.exit(0)

if __name__ == '__main__':
    main()
