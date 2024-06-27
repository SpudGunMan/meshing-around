#!/bin/bash
# set virtual environment and install dependencies
#python -m venv venv
#source venv/bin/activate
pip install -r requirements.txt

echo "Which bot do you want to install? (pong/mesh)"
read bot

if [ $bot == "pong" ]; then
    # install service for pong bot
    sudo cp etc/pong_bot.service /etc/systemd/system/
    exit 0
fi

if [ $bot == "mesh" ]; then
    # install service for mesh bot
    sudo cp etc/mesh_bot.service /etc/systemd/system/
    exit 0
fi

# reminder to change the .service file to proper path for the bot