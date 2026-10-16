# Source this file to set the local environment for the app and Airflow. No secrets here.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
export CAPMON_HOME="$ROOT"
export PATH="$ROOT/.venv/bin:$PATH"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export AIRFLOW_HOME="$ROOT/airflow_home"
export AIRFLOW__CORE__DAGS_FOLDER="$ROOT/airflow/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export AIRFLOW__CORE__DEFAULT_TIMEZONE=America/New_York
export AIRFLOW__API__PORT=8080
export AIRFLOW__API__HOST=127.0.0.1
export AIRFLOW__DAG_PROCESSOR__REFRESH_INTERVAL=30
export AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL=30
export CAPMON_AIRFLOW_URL="http://127.0.0.1:8080"
export CAPMON_APP_PORT="${CAPMON_APP_PORT:-5055}"
export NO_PROXY=127.0.0.1,localhost
