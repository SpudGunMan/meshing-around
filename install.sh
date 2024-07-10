#!/bin/bash

# install.sh

cd "$(dirname "$0")"

# set virtual environment and install dependencies

echo "Do you want to install the bot in a virtual environment? (y/n)"
read venv

if [ $venv == "n" ]; then
    # install dependencies
    echo "Are you on Raspberry Pi? should we add --break-system-packages to the pip install command? (y/n)"
    read rpi
    if [ $rpi == "y" ]; then
        pip install -U -r requirements.txt --break-system-packages
    else
        pip install -U -r requirements.txt
    fi
fi

if [ $venv == "y" ]; then
    # set virtual environment
    python -m venv venv
    source venv/bin/activate

    # install dependencies
    pip install -U -r requirements.txt
fi

echo "Which bot do you want to install as a service? (pong/mesh/n)"
read bot


# reminder to change the .service file to proper path for the bot

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

if [ $bot == "n" ]; then
    launch.sh
    exit 0
fi

echo "Goodbye!"
exit 0
