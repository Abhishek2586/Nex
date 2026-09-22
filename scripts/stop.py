"""Stop only the NEXORA process recorded by the controlled launcher."""
import json
import socket
import time
from pathlib import Path
import psutil

root = Path(__file__).resolve().parents[1]
manifest = root / 'runtime/control/process.json'

def verify_ports_free(ports):
    occupied = []
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(('127.0.0.1', port)) == 0:
                occupied.append(port)
    return occupied

def main():
    if not manifest.exists():
        print('No owned NEXORA process is recorded.')
    
    ports_to_check = [8080, 8082, 8083, 8100]
    record = {}
    if manifest.exists():
        try:
            record = json.loads(manifest.read_text())
            ports_to_check = [
                record.get('port', 8080)
            ]
            for child in record.get('children', []):
                if 'port' in child:
                    ports_to_check.append(child['port'])
        except (json.JSONDecodeError, OSError):
            manifest.unlink(missing_ok=True)
    
    procs = []
    
    for child in record.get('children', []):
        try:
            p = psutil.Process(int(child['pid']))
            cmd = ' '.join(p.cmdline()).lower()
            if Path(p.cwd()).resolve() == root.resolve() and 'app' in cmd:
                procs.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            pass
            
    if 'pid' in record:
        try:
            p = psutil.Process(int(record['pid']))
            cmd = ' '.join(p.cmdline()).lower()
            if Path(p.cwd()).resolve() == root.resolve() and 'scripts/start.py' in cmd.replace('\\', '/'):
                procs.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            pass

    if not procs and manifest.exists():
        manifest.unlink(missing_ok=True)
        print('Removed stale NEXORA process record.')
        
    for p in procs:
        try:
            p.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            pass
            
    gone, alive = psutil.wait_procs(procs, timeout=10)
    for p in alive:
        print(f'Force killing NEXORA process {p.pid}')
        try:
            p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            pass
            
    if alive:
        psutil.wait_procs(alive, timeout=5)
        
    manifest.unlink(missing_ok=True)
    
    if procs:
        print(f'Stopped {len(procs)} owned NEXORA processes.')
        
    # Brief pause to ensure OS releases ports
    time.sleep(1)
    
    occupied = verify_ports_free(ports_to_check)
    if occupied:
        print(f'Warning: Ports {occupied} are still occupied by unrelated processes!')
        raise SystemExit(1)
    else:
        print(f'Verified ports {ports_to_check} are free.')

if __name__ == '__main__':
    main()
