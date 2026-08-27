#!/usr/bin/env bash
# Launch the Red Team Mastery Tracker backend using the project venv.
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$DIR/.venv/bin/python"
[ -x "$PY" ] || PY="python3"
exec "$PY" "$DIR/server.py" "$@"
