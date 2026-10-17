#!/bin/sh
# Write manifest.json on THIS machine, then commit it. Do not run this in CI.
set -eu
cd "$(dirname "$0")"
if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then
  PY=.venv/Scripts/python.exe
else
  PY=python
fi
exec "$PY" scripts/write_manifest.py
