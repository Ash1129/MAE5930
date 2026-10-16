#!/bin/bash
# Starts the Airflow scheduler + API server locally (standalone mode) in the background.
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$ROOT"
mkdir -p logs "$AIRFLOW_HOME"
if [ -f logs/airflow.pid ] && kill -0 "$(cat logs/airflow.pid)" 2>/dev/null; then
  echo "Airflow already running (pid $(cat logs/airflow.pid))"; exit 0
fi
nohup .venv/bin/airflow standalone > logs/airflow.log 2>&1 &
echo $! > logs/airflow.pid
echo "Airflow starting (pid $!). UI: http://127.0.0.1:8080  log: logs/airflow.log"
