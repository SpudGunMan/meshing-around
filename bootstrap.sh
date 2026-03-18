#!/usr/bin/env bash
set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$BASE_DIR"

if [[ ! -d "$BASE_DIR/venv" ]]; then
	python3 -m venv "$BASE_DIR/venv"
fi

source "$BASE_DIR/venv/bin/activate"
"$BASE_DIR/venv/bin/pip" install -r "$BASE_DIR/requirements.txt"

mkdir -p "$BASE_DIR/data"
cp -Rn "$BASE_DIR/etc/data/." "$BASE_DIR/data/"

if [[ ! -f "$BASE_DIR/config.ini" ]]; then
	cp "$BASE_DIR/config.template" "$BASE_DIR/config.ini"
	sleep 1
	replace="s|type = serial|type = tcp|g"
	sed -i '' "$replace" "$BASE_DIR/config.ini"
	replace="s|# hostname = meshtastic.local|hostname = localhost|g"
	sed -i '' "$replace" "$BASE_DIR/config.ini"
else
	echo "config.ini already exists, leaving it unchanged."
fi

deactivate
