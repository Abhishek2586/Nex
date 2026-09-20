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
    if not (root/'frontend/dist/index.html').exists() or not (root/'models/neural/metadata.json').exists():
        raise SystemExit('Prepared frontend/model artifacts are missing. Run the preparation commands documented in README.md.')
    manifest=root/'runtime/control/process.json'; manifest.parent.mkdir(parents=True,exist_ok=True)
    coordinator_command=[sys.executable,'-m','uvicorn','nexora.federation.coordinator:app','--host','127.0.0.1','--port','8100']
    ssl_options={}
    if args.profile=='secure-demo':
        subprocess.run([sys.executable,'scripts/generate_local_certs.py'],cwd=root,check=True)
        certs=root/'runtime/control/certs'; os.environ['NEXORA_COORDINATOR_URL']='https://127.0.0.1:8100'; os.environ['NEXORA_CA_FILE']=str(certs/'ca.pem')
        coordinator_command += ['--ssl-keyfile',str(certs/'server.key'),'--ssl-certfile',str(certs/'server.pem')]
        ssl_options={'ssl_keyfile':str(certs/'server.key'),'ssl_certfile':str(certs/'server.pem')}
    else:
        os.environ['NEXORA_COORDINATOR_URL']='http://127.0.0.1:8100'; os.environ.pop('NEXORA_CA_FILE',None)
    coordinator=subprocess.Popen(coordinator_command,cwd=root,env=os.environ.copy())
    manifest.write_text(json.dumps({'pid':os.getpid(),'command':'scripts/start.py','host':'127.0.0.1','port':args.port,'profile':args.profile,'children':[{'pid':coordinator.pid,'role':'coordinator','port':8100}]},indent=2))
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
        try:
            current=json.loads(manifest.read_text())
            if current.get('pid')==os.getpid(): manifest.unlink()
        except (FileNotFoundError,json.JSONDecodeError,OSError): pass
