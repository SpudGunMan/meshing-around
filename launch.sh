#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ ! -x venv/bin/python ]]; then
    echo "Virtual environment missing. Run: bash bootstrap.sh" >&2
    exit 1
fi
exec venv/bin/python mesh_bot.py "$@"
