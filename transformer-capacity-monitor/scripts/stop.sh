#!/bin/bash
# Stops the review app and Airflow.
source "$(dirname "$0")/env.sh"
cd "$ROOT"
for name in app airflow; do
  if [ -f "logs/$name.pid" ]; then
    pid=$(cat "logs/$name.pid")
    if kill -0 "$pid" 2>/dev/null; then pkill -TERM -P "$pid" 2>/dev/null; kill -TERM "$pid" 2>/dev/null; echo "stopped $name (pid $pid)"; fi
    rm -f "logs/$name.pid"
  fi
done
# Airflow standalone spawns child processes; make sure none linger.
pkill -f "airflow (scheduler|api-server|dag-processor|triggerer|standalone)" 2>/dev/null || true
echo "done"
