#!/bin/bash
# Starts the review app (Flask) in the background on http://127.0.0.1:5055
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$ROOT"
mkdir -p logs
if [ -f logs/app.pid ] && kill -0 "$(cat logs/app.pid)" 2>/dev/null; then
  echo "Review app already running (pid $(cat logs/app.pid))"; exit 0
fi
nohup .venv/bin/python -m webapp.app > logs/app.log 2>&1 &
echo $! > logs/app.pid
echo "Review app starting (pid $!). Open http://127.0.0.1:$CAPMON_APP_PORT  log: logs/app.log"
