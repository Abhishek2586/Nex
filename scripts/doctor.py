import importlib.util, json, platform, shutil, subprocess, sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
modules=['fastapi','uvicorn','sqlalchemy','numpy','scipy','pandas','sklearn','torch','opacus','captum','shap','safetensors']
report={
    'platform':platform.platform(), 'python':sys.version.split()[0],
    'node':subprocess.run(['node','--version'],capture_output=True,text=True).stdout.strip(),
    'npm':subprocess.run(['npm.cmd' if sys.platform == 'win32' else 'npm','--version'],capture_output=True,text=True).stdout.strip(),
    'disk_free_gb':round(shutil.disk_usage(root).free/1024**3,2),
    'imports':{name:importlib.util.find_spec(name) is not None for name in modules},
    'frontend_built':(root/'frontend/dist/index.html').exists(),
    'models_prepared':(root/'models/registry/active.json').exists(),
    'wesad_status':'unavailable' if not (root/'data/raw/wesad').exists() else 'files_present_not_validated',
}
print(json.dumps(report,indent=2))
raise SystemExit(0 if all(report['imports'].values()) and report['frontend_built'] and report['models_prepared'] else 1)
