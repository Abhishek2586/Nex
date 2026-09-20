import json
import zipfile
from scripts.build_evidence import build


def test_export_has_checksums_and_excludes_sensitive_paths():
    output, manifest = build()
    assert manifest["files"]
    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        exported = json.loads(archive.read("export-manifest.json"))
    assert exported["files"] == manifest["files"]
    assert not any(".env" in name or name.endswith((".key", ".pem", ".sqlite")) for name in names)
