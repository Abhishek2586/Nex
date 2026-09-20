"""Restart only the coordinator child owned by the active NEXORA launcher."""
import json
import os
from pathlib import Path
import subprocess
import sys
import psutil
import argparse

parser=argparse.ArgumentParser(description='Restart or stop the owned local coordinator')
parser.add_argument('--stop-only',action='store_true')
args=parser.parse_args()

root=Path(__file__).resolve().parents[1]
manifest=root/'runtime/control/process.json'
if not manifest.exists(): raise SystemExit('NEXORA launcher is not running.')
record=json.loads(manifest.read_text())
for child in record.get('children',[]):
    if child.get('role')!='coordinator': continue
    try:
        process=psutil.Process(int(child['pid']))
        command=' '.join(process.cmdline()).lower()
        if Path(process.cwd()).resolve()==root.resolve() and 'nexora.federation.coordinator:app' in command:
            process.terminate()
            try: process.wait(timeout=10)
            except psutil.TimeoutExpired: raise SystemExit('Coordinator did not stop cleanly.')
    except psutil.NoSuchProcess: pass
if args.stop_only:
    print('Stopped the owned coordinator; edge service remains running.')
    raise SystemExit(0)
environment=os.environ.copy(); environment['PYTHONPATH']=str(root/'src')
process=subprocess.Popen([sys.executable,'-m','uvicorn','nexora.federation.coordinator:app','--host','127.0.0.1','--port','8100'],cwd=root,env=environment)
record['children']=[item for item in record.get('children',[]) if item.get('role')!='coordinator']
record['children'].append({'pid':process.pid,'role':'coordinator','port':8100})
manifest.write_text(json.dumps(record,indent=2))
print(f'Restarted coordinator as owned process {process.pid}.')
