#!/usr/bin/env python3
"""
NEXORA Bootstrap Script
Idempotent setup for the local development and demonstration environment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.resolve()

def run_command(cmd, cwd=ROOT_DIR, check=True):
    print(f"Running: {' '.join(cmd)} in {cwd}")
    # On Windows, setting shell=True helps with npm if it's a .cmd script
    shell = os.name == 'nt' and cmd[0] == 'npm'
    subprocess.run(cmd, cwd=cwd, check=check, shell=shell)

def main():
    print("Starting NEXORA Bootstrap...")

    # 1. Create directories
    dirs = ["data", "runtime", "models", "artifacts"]
    for d in dirs:
        (ROOT_DIR / d).mkdir(exist_ok=True)
        print(f"Ensured directory exists: {d}/")

    # 2. Virtual environment
    venv_dir = ROOT_DIR / ".venv"
    if not venv_dir.exists():
        print("Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", ".venv"])
    
    # 3. Determine pip path
    if os.name == 'nt':
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_exe = venv_dir / "bin" / "pip"

    if not pip_exe.exists():
        print(f"Error: pip not found at {pip_exe}")
        sys.exit(1)

    # 4. Install dependencies
    print("Installing Python dependencies...")
    run_command([str(pip_exe), "install", "-e", "."])

    # 5. Frontend dependencies
    frontend_dir = ROOT_DIR / "frontend"
    if frontend_dir.exists():
        print("Installing frontend dependencies...")
        run_command(["npm", "install"], cwd=frontend_dir)
        print("Installing Playwright browsers...")
        run_command(["npx", "playwright", "install", "--with-deps", "chromium"], cwd=frontend_dir)
        print("Building frontend...")
        run_command(["npm", "run", "build"], cwd=frontend_dir)
    else:
        print("Warning: frontend directory not found.")

    # 6. Copy .env
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"
    if not env_file.exists() and env_example.exists():
        print("Copying .env.example to .env...")
        shutil.copy(env_example, env_file)

    print("\nBootstrap complete. You can now run the system using the appropriate start script.")

if __name__ == "__main__":
    main()
