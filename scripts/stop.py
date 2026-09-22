"""Stop only the NEXORA process recorded by the controlled launcher."""
import json
from pathlib import Path
import psutil

root=Path(__file__).resolve().parents[1]
manifest=root/'runtime/control/process.json'
if not manifest.exists():
    print('No owned NEXORA process is recorded.')
    raise SystemExit(0)
record=json.loads(manifest.read_text())
for child in record.get('children',[]):
    try:
        child_process=psutil.Process(int(child['pid']))
        child_command=' '.join(child_process.cmdline()).lower()
        child_cwd=Path(child_process.cwd()).resolve()
        role=child.get('role')
        expected_module = 'nexora.federation.coordinator:app' if role == 'coordinator' else 'nexora.edge.app:app'
        if role in {'coordinator', 'client-b', 'client-c'} and child_cwd==root.resolve() and expected_module in child_command:
            child_process.terminate()
            try: child_process.wait(timeout=10)
            except psutil.TimeoutExpired: pass
    except (psutil.NoSuchProcess,psutil.AccessDenied,OSError): pass
pid=int(record['pid'])
try:
    process=psutil.Process(pid)
    command=' '.join(process.cmdline()).lower()
    process_cwd=Path(process.cwd()).resolve()
except (psutil.NoSuchProcess,psutil.AccessDenied,OSError):
    manifest.unlink(missing_ok=True)
    print('Removed stale NEXORA process record.')
    raise SystemExit(0)
if process_cwd!=root.resolve() or 'scripts/start.py' not in command.replace('\\','/'):
    raise SystemExit('Refusing to terminate a process that does not match the recorded NEXORA launcher.')
process.terminate()
try: process.wait(timeout=10)
except psutil.TimeoutExpired:
    raise SystemExit('NEXORA did not stop within 10 seconds; process was not force-killed.')
manifest.unlink(missing_ok=True)
print(f'Stopped owned NEXORA process {pid}.')
