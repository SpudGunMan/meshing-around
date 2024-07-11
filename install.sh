#!/bin/bash

# install.sh
cd "$(dirname "$0")"

# add user to groups for serial access
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER

# generate config file
cp config.template config.ini

# set virtual environment and install dependencies
printf "\nMeshing Around Installer\n"
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
printf "\n\n"
echo "Which bot do you want to install as a service? (pong/mesh/n)"
read bot


# reminder to change the .service file to proper path for the bot

#set the correct path in the service file
program_path=$(pwd)
cp etc/pong_bot.tmp etc/pong_bot.service
cp etc/mesh_bot.tmp etc/mesh_bot.service
replace="s|/dir/|$program_path/|g"
sed -i $replace etc/pong_bot.service
sed -i $replace etc/mesh_bot.service

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
    if [ -f launch.sh ]; then
        ./launch.sh
fi

echo "Goodbye!"
exit 0
