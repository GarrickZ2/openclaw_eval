#!/usr/bin/env bash

set -euo pipefail

demo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
api_dir="$demo_root/apps/api"
web_dir="$demo_root/apps/web"
api_pid=""
web_pid=""

cleanup() {
  echo
  echo "Stopping Pinch Router Lab…"
  [[ -n "$api_pid" ]] && kill "$api_pid" 2>/dev/null || true
  [[ -n "$web_pid" ]] && kill "$web_pid" 2>/dev/null || true
  wait 2>/dev/null || true
}

wait_for_url() {
  local check_url="$1"
  local service_name="$2"
  local tries=40
  until curl --silent --fail "$check_url" >/dev/null; do
    tries=$((tries - 1))
    if [[ "$tries" -eq 0 ]]; then
      echo "Timed out waiting for $service_name at $check_url" >&2
      exit 1
    fi
    sleep 1
  done
}

trap cleanup EXIT INT TERM

if [[ ! -d "$web_dir/node_modules" ]]; then
  echo "Installing web dependencies…"
  (cd "$web_dir" && npm install)
fi

echo "Starting API on http://127.0.0.1:8000"
(cd "$api_dir" && uv run pinch-api) &
api_pid=$!

echo "Starting web app on http://127.0.0.1:5173"
(cd "$web_dir" && npm run dev -- --host 127.0.0.1 --port 5173) &
web_pid=$!

wait_for_url "http://127.0.0.1:8000/api/health" "API"
wait_for_url "http://127.0.0.1:5173" "web app"

echo
echo "Pinch Router Lab is ready: http://127.0.0.1:5173"
echo "Press Ctrl+C to stop both services."
open "http://127.0.0.1:5173"

wait
