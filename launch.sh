#!/bin/bash

# launch.sh
echo "Launches the bot in a virtual environment"

# activate the virtual environment

#look for venv folder and activate it if found
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# launch the application

python mesh_bot.py
#python pong_bot.py