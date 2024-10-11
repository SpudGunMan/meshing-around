#!/bin/bash

# launch.sh
cd "$(dirname "$0")"

# activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

if [ ! -f "config.ini" ]; then
    cp config.template config.ini
fi

# launch the application
if [ "$1" == "pong" ]; then
    python3 pong_bot.py
elif [ "$1" == "mesh" ]; then
    python3 mesh_bot.py
elif [ "$1" == "html" ]; then
    python3 etc/report_generator.py
elif [ "$1" == "html5" ]; then
    python3 etc/report_generator5.py
else
    echo "Please provide a bot to launch (pong/mesh) or a report to generate (html/html5)"
    exit 1
fi

deactivate