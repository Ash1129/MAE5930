#!/bin/bash
source "$(dirname "$0")/env.sh"
cd "$ROOT"
for name in app airflow; do
  if [ -f "logs/$name.pid" ] && kill -0 "$(cat logs/$name.pid)" 2>/dev/null; then echo "$name: running (pid $(cat logs/$name.pid))"; else echo "$name: stopped"; fi
done
curl -s -o /dev/null -w "review app http://127.0.0.1:$CAPMON_APP_PORT -> HTTP %{http_code}\n" "http://127.0.0.1:$CAPMON_APP_PORT/" || true
curl -s -o /dev/null -w "airflow http://127.0.0.1:8080 -> HTTP %{http_code}\n" "http://127.0.0.1:8080/" || true
