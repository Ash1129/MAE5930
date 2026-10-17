"""Write manifest.json for Posit Connect. Run on a developer machine, then commit the result.

Calling the library directly avoids a Windows shell bug that turns `.venv/**` into extra files.
Checksums are then rewritten to the bytes GitHub will check out (LF text, committed binaries),
because this machine's working tree uses CRLF.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from rsconnect.bundle import write_api_manifest_json
from rsconnect.environment import Environment
from rsconnect.models import AppModes

# Local edits that must not be part of the published bundle.
KEEP_HEAD = {
    "data/capacity_monitor.sqlite3",
    "data/reports/2026-10-15/report.html",
    "data/reports/2026-10-15/report.json",
    "data/reports/2026-10-15/report.md",
}

environment = Environment.create_python_environment(
    ".",
    requirements_file="requirements.txt",
    python=sys.executable,
    override_python_version="3.12.4",
    app_file="app.py",
)
write_api_manifest_json(
    ".",
    "app:app",
    environment,
    AppModes.PYTHON_API,
    [],
    [
        ".venv/**",
        "airflow_home/**",
        "logs/**",
        "**/__pycache__/*",
        "**/*.pyc",
        ".pytest_cache/**",
        "data/work/**",
        "data/reports/*/history/**",
        "data/*.sqlite3-wal",
        "data/*.sqlite3-shm",
        "scripts/write_manifest.py",
    ],
)
def _payload(rel: str) -> bytes:
    repo_rel = "transformer-capacity-monitor/" + rel.replace("\\", "/")
    if rel.replace("\\", "/") in KEEP_HEAD:
        return subprocess.check_output(["git", "show", f"HEAD:{repo_rel}"])
    data = Path(rel).read_bytes()
    if b"\0" in data[:8192]:
        return data
    return data.replace(b"\r\n", b"\n")


manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["files"] = {
    rel: info for rel, info in manifest["files"].items() if "__pycache__" not in rel.replace("\\", "/") and not rel.endswith(".pyc")
}
# Keep the published locale. This Windows machine would otherwise record its own code page.
manifest["locale"] = "en_US.UTF-8"
for rel, info in manifest["files"].items():
    info["checksum"] = hashlib.md5(_payload(rel)).hexdigest()
manifest_path.write_bytes(json.dumps(manifest, indent=2).encode("utf-8") + b"\n")
print("wrote manifest.json")
