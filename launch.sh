#!/bin/bash

# launch.sh
cd "$(dirname "$0")"

printf "\n\nLaunches the bot in a virtual environment"

# activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# launch the application


if [ "$1" == "pong" ]; then
    python pong_bot.py
elif [ "$1" == "mesh" ]; then
    python mesh_bot.py
else
    echo "Please provide a bot to launch (pong/mesh)"
fi
