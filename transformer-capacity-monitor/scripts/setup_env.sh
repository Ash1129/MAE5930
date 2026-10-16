#!/bin/bash
# One-time local setup: creates .venv and installs Apache Airflow 3 (scheduler) + Flask (review app).
# Safe to re-run. No network accounts or paid services are involved.
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required (https://docs.astral.sh/uv/). On macOS: brew install uv" >&2
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  uv venv .venv --python 3.12
fi
uv pip install --python .venv/bin/python "apache-airflow[standard]>=3.0,<4" "flask>=3,<4" pytest
.venv/bin/python -c "import airflow, flask; print('airflow', airflow.__version__, '| flask', flask.__version__)"
