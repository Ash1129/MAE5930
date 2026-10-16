#!/bin/bash
# Double-click launcher (macOS). Starts the scheduler and the review app, then opens the app.
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "First-time setup: installing Airflow and the review app into .venv (a few minutes)..."
  ./scripts/setup_env.sh || { echo "Setup failed; see above."; read -r -p "Press Enter to close"; exit 1; }
fi
if [ ! -f data/feeds/readings.csv ]; then
  echo "Generating synthetic sample feeds (500 transformers)..."
  .venv/bin/python scripts/make_synthetic_data.py --count 500
fi
./scripts/start_airflow.sh
./scripts/start_app.sh
sleep 3
open "http://127.0.0.1:5055/"
echo "Capacity Monitor is running. You can close this window; use 'Stop Capacity Monitor.command' to stop."
