#!/usr/bin/env bash
# NEXORA Start Script (Bash wrapper)
# Usage: bash scripts/start.sh [--profile demo]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

VENV_PYTHON="$ROOT/.venv/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
    echo "ERROR: Virtual environment not found at .venv/. Run scripts/bootstrap.sh first."
    exit 1
fi

echo "Starting NEXORA with Python: $VENV_PYTHON"
exec "$VENV_PYTHON" "$ROOT/scripts/start.py" "$@"
