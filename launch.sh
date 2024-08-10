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
else
    printf "\nPlease provide a bot to launch (pong/mesh)"
fi

deactivate