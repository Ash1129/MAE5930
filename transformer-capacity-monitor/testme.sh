#!/bin/sh
# Run the review app locally. One command, no arguments.
set -eu
cd "$(dirname "$0")"
if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then
  PY=.venv/Scripts/python.exe
else
  PY=python
fi
exec "$PY" -m webapp.app
