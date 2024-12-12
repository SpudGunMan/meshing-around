#!/bin/bash
# This script launches the meshing-around bot or the report generator in python virtual environment

# launch.sh
cd "$(dirname "$0")"


if [ ! -f "config.ini" ]; then
    cp config.template config.ini
fi

# activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found, this tool just launches the .py in venv"
    exit 1
fi

# launch the application
if [[ "$1" == pong* ]]; then
    python3 pong_bot.py
elif [[ "$1" == mesh* ]]; then
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