#!/usr/bin/env bash
# NEXORA Bootstrap Script (Bash wrapper for Linux/macOS)
# Usage: bash scripts/bootstrap.sh
# Or:    ./scripts/bootstrap.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

echo "NEXORA Bootstrap (Bash wrapper)"
echo "Delegating to scripts/bootstrap.py ..."

# Find a suitable Python 3.11+
PYTHON_EXE=""
VENV_PYTHON="$ROOT/.venv/bin/python"

if [ -x "$VENV_PYTHON" ]; then
    PYTHON_EXE="$VENV_PYTHON"
else
    for candidate in python3.11 python3.12 python3.13 python3 python; do
        if command -v "$candidate" &>/dev/null; then
            version=$("$candidate" -c "import sys; print(sys.version_info[:2])" 2>/dev/null)
            if echo "$version" in *"(3, 11)"* *"(3, 12)"* *"(3, 13)"*; then
                PYTHON_EXE="$candidate"
                break
            fi
            # Simple version check
            if "$candidate" -c "import sys; assert sys.version_info >= (3, 11)" 2>/dev/null; then
                PYTHON_EXE="$candidate"
                break
            fi
        fi
    done
fi

if [ -z "$PYTHON_EXE" ]; then
    echo "ERROR: Python 3.11+ not found. Install Python and re-run."
    exit 1
fi

echo "Using Python: $PYTHON_EXE"
exec "$PYTHON_EXE" "$ROOT/scripts/bootstrap.py" "$@"
