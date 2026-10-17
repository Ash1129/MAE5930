#!/bin/sh
# Publish this folder to the course Posit Connect server.
# Put CONNECT_SERVER and CONNECT_API_KEY in a gitignored .env first.
set -eu
cd "$(dirname "$0")"
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi
if [ -z "${CONNECT_SERVER:-}" ] || [ -z "${CONNECT_API_KEY:-}" ]; then
  echo "Set CONNECT_SERVER and CONNECT_API_KEY in .env (see .env.example). Do not commit .env." >&2
  exit 1
fi
rsconnect add --server "$CONNECT_SERVER" --api-key "$CONNECT_API_KEY" --name connect
exec rsconnect deploy flask --server connect --entrypoint app:app .
