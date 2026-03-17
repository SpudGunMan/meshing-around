#!/usr/bin/env bash
set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$BASE_DIR"
python3 -m venv "$BASE_DIR/venv"
source "$BASE_DIR/venv/bin/activate"
"$BASE_DIR/venv/bin/pip" install -r "$BASE_DIR/requirements.txt"
cp -r "$BASE_DIR/etc/data/." "$BASE_DIR/data/"
cp "$BASE_DIR/etc/config.template" "$BASE_DIR/config.ini"
replace="s|type = serial|type = tcp|g"
sed -i '' "$replace" "$BASE_DIR/config.ini"
replace="s|# hostname = meshtastic.local|hostname = localhost|g"
sed -i '' "$replace" "$BASE_DIR/config.ini"
deactivate
