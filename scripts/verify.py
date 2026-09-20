import os, subprocess, sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
environment=os.environ.copy()
environment['PYTHONPATH']=str(root/'src')+os.pathsep+str(root)
environment['MPLCONFIGDIR']=str(root/'runtime/matplotlib')
commands=[
    [sys.executable,'-m','pytest','-q'],
    ['npm.cmd','run','build'],
    [sys.executable,'scripts/build_evidence.py'],
]
for command in commands:
    completed=subprocess.run(command,cwd=root/'frontend' if command[0]=='npm.cmd' else root,env=environment)
    if completed.returncode: raise SystemExit(completed.returncode)
print('NEXORA current verification passed.')
