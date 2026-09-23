import argparse, json, os, subprocess, sys, socket, time
import urllib.request
import psutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
os.chdir(root)
os.environ['PYTHONPATH'] = str(root / 'src')
os.environ['MPLCONFIGDIR'] = str(root / 'runtime/matplotlib')
sys.path.insert(0, str(root / 'src'))

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def get_pid_using_port(port):
    try:
        for conn in psutil.net_connections(kind='tcp'):
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return conn.pid
    except (psutil.AccessDenied, OSError):
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description='Start the prepared NEXORA local demo')
    parser.add_argument('--profile', choices=['demo', 'dev', 'low-resource', 'secure-demo'], default='demo')
    parser.add_argument('--port', type=int, default=8080, help='Dashboard port')
    parser.add_argument('--port-b', type=int, default=8082, help='Client-b port')
    parser.add_argument('--port-c', type=int, default=8083, help='Client-c port')
    parser.add_argument('--coordinator-port', type=int, default=8100, help='Coordinator port')
    parser.add_argument('--restart', action='store_true', help='Restart running NEXORA processes')
    args = parser.parse_args()
    
    if not (root / 'frontend/dist/index.html').exists():
        raise SystemExit('Prepared frontend artifacts are missing. Run the preparation commands documented in README.md.')
        
    manifest = root / 'runtime/control/process.json'
    manifest.parent.mkdir(parents=True, exist_ok=True)
    
    # 1. Inspect process.json
    valid_running = False
    if manifest.exists():
        try:
            record = json.loads(manifest.read_text())
            if 'pid' in record:
                p = psutil.Process(int(record['pid']))
                cmd = ' '.join(p.cmdline()).lower()
                if Path(p.cwd()).resolve() == root.resolve() and 'scripts/start.py' in cmd.replace('\\', '/'):
                    valid_running = True
        except (json.JSONDecodeError, OSError, psutil.NoSuchProcess, psutil.AccessDenied):
            manifest.unlink(missing_ok=True) # Stale manifest
            print('Removed stale NEXORA process record.')
            
    if valid_running:
        if args.restart:
            print('Stopping existing NEXORA stack...')
            subprocess.run([sys.executable, 'scripts/stop.py'], cwd=root, check=True)
        else:
            try:
                record = json.loads(manifest.read_text())
                running_port = record.get('port', args.port)
                print(f'NEXORA is already running at http://127.0.0.1:{running_port}')
            except Exception:
                print(f'NEXORA is already running at http://127.0.0.1:{args.port}')
            sys.exit(0)
            
    # 3. Detect whether ports are occupied
    ports_needed = [args.port, args.port_b, args.port_c, args.coordinator_port]
    occupied_by_others = False
    for p in ports_needed:
        if is_port_in_use(p):
            pid = get_pid_using_port(p)
            print(f'Error: Port {p} is already occupied by PID {pid or "unknown"} (not owned by this NEXORA instance).')
            occupied_by_others = True
            
    if occupied_by_others:
        raise SystemExit('Cannot start: One or more required ports are occupied by unrelated processes.')
        
    import secrets
    tokens = {
        'coordinator': secrets.token_hex(32),
        'client-a': secrets.token_hex(32),
        'client-b': secrets.token_hex(32),
        'client-c': secrets.token_hex(32)
    }
    (root / 'runtime/control/tokens.json').write_text(json.dumps(tokens, indent=2))
    
    coordinator_command = [sys.executable, '-m', 'uvicorn', 'nexora.federation.coordinator:app', '--host', '127.0.0.1', '--port', str(args.coordinator_port)]
    ssl_options = {}
    
    env_a = os.environ.copy()
    env_a['NEXORA_CLIENT'] = 'client-a'
    env_b = os.environ.copy()
    env_b['NEXORA_CLIENT'] = 'client-b'
    env_c = os.environ.copy()
    env_c['NEXORA_CLIENT'] = 'client-c'

    if args.profile == 'secure-demo':
        subprocess.run([sys.executable, 'scripts/generate_local_certs.py'], cwd=root, check=True)
        certs = root / 'runtime/control/certs'
        os.environ['NEXORA_COORDINATOR_URL'] = f'https://127.0.0.1:{args.coordinator_port}'
        os.environ['NEXORA_CLIENT_A_URL'] = f'https://127.0.0.1:{args.port}'
        os.environ['NEXORA_CLIENT_B_URL'] = f'https://127.0.0.1:{args.port_b}'
        os.environ['NEXORA_CLIENT_C_URL'] = f'https://127.0.0.1:{args.port_c}'
        os.environ['NEXORA_CA_FILE'] = str(certs / 'ca.pem')
        coordinator_command += ['--ssl-keyfile', str(certs / 'server.key'), '--ssl-certfile', str(certs / 'server.pem')]
        ssl_options = {'ssl_keyfile': str(certs / 'server.key'), 'ssl_certfile': str(certs / 'server.pem')}
        env_a['NEXORA_COORDINATOR_URL'] = env_b['NEXORA_COORDINATOR_URL'] = env_c['NEXORA_COORDINATOR_URL'] = f'https://127.0.0.1:{args.coordinator_port}'
        env_a['NEXORA_CA_FILE'] = env_b['NEXORA_CA_FILE'] = env_c['NEXORA_CA_FILE'] = str(certs / 'ca.pem')
    else:
        os.environ['NEXORA_COORDINATOR_URL'] = f'http://127.0.0.1:{args.coordinator_port}'
        os.environ['NEXORA_CLIENT_A_URL'] = f'http://127.0.0.1:{args.port}'
        os.environ['NEXORA_CLIENT_B_URL'] = f'http://127.0.0.1:{args.port_b}'
        os.environ['NEXORA_CLIENT_C_URL'] = f'http://127.0.0.1:{args.port_c}'
        os.environ.pop('NEXORA_CA_FILE', None)
        env_a['NEXORA_COORDINATOR_URL'] = env_b['NEXORA_COORDINATOR_URL'] = env_c['NEXORA_COORDINATOR_URL'] = f'http://127.0.0.1:{args.coordinator_port}'

    def wait_for_health(url, name, ctx=None):
        for _ in range(60):
            try:
                urllib.request.urlopen(url, context=ctx, timeout=5)
                return True
            except Exception:
                time.sleep(0.5)
        return False
        
    coordinator = None
    client_a = None
    client_b = None
    client_c = None
    
    try:
        coordinator = subprocess.Popen(coordinator_command, cwd=root, env=os.environ.copy())
        
        ctx = None
        if ssl_options:
            import ssl
            ctx = ssl.create_default_context(cafile=str(certs / 'ca.pem'))
            
        coord_url = os.environ.get('NEXORA_COORDINATOR_URL') + '/health'
        if not wait_for_health(coord_url, 'coordinator', ctx):
            raise RuntimeError("Coordinator failed to become healthy")
            
        ca_cmd = [sys.executable, '-m', 'uvicorn', 'nexora.edge.app:app', '--host', '127.0.0.1', '--port', str(args.port)]
        cb_cmd = [sys.executable, '-m', 'uvicorn', 'nexora.edge.app:app', '--host', '127.0.0.1', '--port', str(args.port_b)]
        cc_cmd = [sys.executable, '-m', 'uvicorn', 'nexora.edge.app:app', '--host', '127.0.0.1', '--port', str(args.port_c)]
        if ssl_options:
            ca_cmd += ['--ssl-keyfile', ssl_options['ssl_keyfile'], '--ssl-certfile', ssl_options['ssl_certfile']]
            cb_cmd += ['--ssl-keyfile', ssl_options['ssl_keyfile'], '--ssl-certfile', ssl_options['ssl_certfile']]
            cc_cmd += ['--ssl-keyfile', ssl_options['ssl_keyfile'], '--ssl-certfile', ssl_options['ssl_certfile']]
            
        client_b = subprocess.Popen(cb_cmd, cwd=root, env=env_b)
        client_c = subprocess.Popen(cc_cmd, cwd=root, env=env_c)
        
        scheme = 'https' if args.profile == 'secure-demo' else 'http'
        b_url = f'{scheme}://127.0.0.1:{args.port_b}/api/v1/health'
        c_url = f'{scheme}://127.0.0.1:{args.port_c}/api/v1/health'
        
        if not wait_for_health(b_url, 'client-b', ctx) or not wait_for_health(c_url, 'client-c', ctx):
            raise RuntimeError("Client processes failed to become healthy")
            
        client_a = subprocess.Popen(ca_cmd, cwd=root, env=env_a)
        a_url = f'{scheme}://127.0.0.1:{args.port}/api/v1/health'
        if not wait_for_health(a_url, 'client-a', ctx):
            raise RuntimeError("Dashboard failed to become healthy")
            
        manifest.write_text(json.dumps({
            'pid': os.getpid(),
            'command': 'scripts/start.py',
            'host': '127.0.0.1',
            'port': args.port,
            'profile': args.profile,
            'children': [
                {'pid': coordinator.pid, 'role': 'coordinator', 'port': args.coordinator_port}, 
                {'pid': client_b.pid, 'role': 'client-b', 'port': args.port_b}, 
                {'pid': client_c.pid, 'role': 'client-c', 'port': args.port_c},
                {'pid': client_a.pid, 'role': 'client-a', 'port': args.port}
            ]
        }, indent=2))
        
        print(f'NEXORA dashboard: {scheme}://127.0.0.1:{args.port}')
        
        # Keep launcher alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    except Exception as e:
        print(f"Startup failed: {e}")
        sys.exit(1)
    finally:
        for p in [coordinator, client_b, client_c, client_a]:
            if p and p.poll() is None:
                p.terminate()
                try: 
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
                    
        try:
            current = json.loads(manifest.read_text())
            if current.get('pid') == os.getpid(): 
                manifest.unlink(missing_ok=True)
        except (FileNotFoundError, json.JSONDecodeError, OSError): 
            pass

if __name__ == '__main__':
    main()
