import argparse, json, os, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
os.chdir(root)
os.environ['PYTHONPATH']=str(root/'src')
os.environ['MPLCONFIGDIR']=str(root/'runtime/matplotlib')
sys.path.insert(0,str(root/'src'))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Start the prepared NEXORA local demo')
    parser.add_argument('--profile',choices=['demo','dev','low-resource','secure-demo'],default='demo')
    parser.add_argument('--port',type=int,default=8080)
    args=parser.parse_args()
    if not (root/'frontend/dist/index.html').exists() or not (root/'models/registry/active.json').exists():
        raise SystemExit('Prepared frontend/model artifacts are missing. Run the preparation commands documented in README.md.')
    manifest=root/'runtime/control/process.json'; manifest.parent.mkdir(parents=True,exist_ok=True)
    
    import secrets
    tokens = {
        'coordinator': secrets.token_hex(32),
        'client-a': secrets.token_hex(32),
        'client-b': secrets.token_hex(32),
        'client-c': secrets.token_hex(32)
    }
    (root/'runtime/control/tokens.json').write_text(json.dumps(tokens, indent=2))
    
    coordinator_command=[sys.executable,'-m','uvicorn','nexora.federation.coordinator:app','--host','127.0.0.1','--port','8100']
    ssl_options={}
    env_b = os.environ.copy()
    env_b['NEXORA_CLIENT'] = 'client-b'
    env_c = os.environ.copy()
    env_c['NEXORA_CLIENT'] = 'client-c'

    if args.profile=='secure-demo':
        subprocess.run([sys.executable,'scripts/generate_local_certs.py'],cwd=root,check=True)
        certs=root/'runtime/control/certs'; os.environ['NEXORA_COORDINATOR_URL']='https://127.0.0.1:8100'; os.environ['NEXORA_CA_FILE']=str(certs/'ca.pem')
        coordinator_command += ['--ssl-keyfile',str(certs/'server.key'),'--ssl-certfile',str(certs/'server.pem')]
        ssl_options={'ssl_keyfile':str(certs/'server.key'),'ssl_certfile':str(certs/'server.pem')}
        env_b['NEXORA_COORDINATOR_URL'] = env_c['NEXORA_COORDINATOR_URL'] = 'https://127.0.0.1:8100'
        env_b['NEXORA_CA_FILE'] = env_c['NEXORA_CA_FILE'] = str(certs/'ca.pem')
    else:
        os.environ['NEXORA_COORDINATOR_URL']='http://127.0.0.1:8100'; os.environ.pop('NEXORA_CA_FILE',None)
        env_b['NEXORA_COORDINATOR_URL'] = env_c['NEXORA_COORDINATOR_URL'] = 'http://127.0.0.1:8100'

    coordinator=subprocess.Popen(coordinator_command,cwd=root,env=os.environ.copy())
    
    # Wait for coordinator to bind
    import time, urllib.request, urllib.error
    coord_url = os.environ.get('NEXORA_COORDINATOR_URL', 'http://127.0.0.1:8100') + '/health'
    for _ in range(30):
        try:
            if ssl_options:
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                urllib.request.urlopen(coord_url, context=ctx)
            else:
                urllib.request.urlopen(coord_url)
            break
        except Exception:
            time.sleep(0.5)
            
    cb_cmd = [sys.executable, '-m', 'uvicorn', 'nexora.edge.app:app', '--host', '127.0.0.1', '--port', '8082']
    cc_cmd = [sys.executable, '-m', 'uvicorn', 'nexora.edge.app:app', '--host', '127.0.0.1', '--port', '8083']
    if ssl_options:
        cb_cmd += ['--ssl-keyfile', ssl_options['ssl_keyfile'], '--ssl-certfile', ssl_options['ssl_certfile']]
        cc_cmd += ['--ssl-keyfile', ssl_options['ssl_keyfile'], '--ssl-certfile', ssl_options['ssl_certfile']]
    
    client_b = subprocess.Popen(cb_cmd, cwd=root, env=env_b)
    client_c = subprocess.Popen(cc_cmd, cwd=root, env=env_c)
    
    manifest.write_text(json.dumps({'pid':os.getpid(),'command':'scripts/start.py','host':'127.0.0.1','port':args.port,'profile':args.profile,'children':[{'pid':coordinator.pid,'role':'coordinator','port':8100}, {'pid': client_b.pid, 'role': 'client-b', 'port': 8082}, {'pid': client_c.pid, 'role': 'client-c', 'port': 8083}]},indent=2))
    scheme='https' if args.profile=='secure-demo' else 'http'
    print(f'NEXORA dashboard: {scheme}://127.0.0.1:{args.port}')
    try:
        import uvicorn
        uvicorn.run('nexora.edge.app:app',host='127.0.0.1',port=args.port,log_level='info',**ssl_options)
    finally:
        if coordinator.poll() is None:
            coordinator.terminate()
            try: coordinator.wait(timeout=10)
            except subprocess.TimeoutExpired: pass
        
        if client_b.poll() is None:
            client_b.terminate()
            try: client_b.wait(timeout=10)
            except subprocess.TimeoutExpired: pass
            
        if client_c.poll() is None:
            client_c.terminate()
            try: client_c.wait(timeout=10)
            except subprocess.TimeoutExpired: pass

        try:
            current=json.loads(manifest.read_text())
            if current.get('pid')==os.getpid(): manifest.unlink()
        except (FileNotFoundError,json.JSONDecodeError,OSError): pass
