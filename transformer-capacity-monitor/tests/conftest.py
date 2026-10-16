import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    """Isolated CAPMON_HOME with synthetic feeds, its own database and report folder."""
    home = tmp_path / "home"
    (home / "rules").mkdir(parents=True)
    for f in ("playbook.json", "decision-table.csv"):
        (home / "rules" / f).write_bytes((ROOT / "rules" / f).read_bytes())
    monkeypatch.setenv("CAPMON_HOME", str(home))
    monkeypatch.delenv("CAPMON_DB", raising=False)
    for mod in [m for m in list(sys.modules) if m.startswith("capacity_monitor") or m.startswith("webapp")]:
        del sys.modules[mod]
    from capacity_monitor import config

    assert config.ROOT == home
    config.ensure_dirs()

    def generate(scenario="normal", end="2026-10-15"):
        env = dict(os.environ, CAPMON_HOME=str(home), PYTHONPATH=str(ROOT))
        subprocess.run([sys.executable, str(ROOT / "scripts" / "make_synthetic_data.py"), "--scenario", scenario, "--end", end], check=True, env=env, capture_output=True)

    generate()
    return {"home": home, "generate": generate}
