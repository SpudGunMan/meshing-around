#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
python3 -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ is required"'
python3 -m venv venv
venv/bin/python -m pip install --no-cache-dir -r requirements.txt
venv/bin/python -m pip check
mkdir -p data
