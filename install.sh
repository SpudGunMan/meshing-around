#!/bin/bash

# install.sh
cd "$(dirname "$0")"

# add user to groups for serial access
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER

# generate config file, check if it exists
if [ -f config.ini ]; then
    printf "\nConfig file already exists, moving to backup config.old\n"
    mv config.ini config.old
fi

cp config.template config.ini
printf "\nConfig file generated\n"


# set virtual environment and install dependencies
printf "\nMeshing Around Installer\n"

#check if python3 has venv module
if ! python3 -m venv --help &> /dev/null
then
    printf "Python3 venv module not found, please install python3-venv with your OS\n"
else
    printf "Python3 venv module found\n"
fi

echo "Do you want to install the bot in a virtual environment? (y/n)"
read venv

if [ $venv == "y" ]; then
    # set virtual environment
    if ! python3 -m venv --help &> /dev/null
    then
        printf "Python3 venv module not found, please install python3-venv with your OS\n"
        exit 1
    else
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate

    # install dependencies
    pip install -U -r requirements.txt
else
    printf "\nSkipping virtual environment...\n"
    # install dependencies
    printf "Are you on Raspberry Pi?\nshould we add --break-system-packages to the pip install command? (y/n)"
    read rpi
    if [ $rpi == "y" ]; then
        pip install -U -r requirements.txt --break-system-packages
    else
        pip install -U -r requirements.txt
    fi
fi

printf "\n\n"
echo "Which bot do you want to install as a service? Pong Mesh or None? (pong/mesh/n)"
read bot

#set the correct path in the service file
program_path=$(pwd)
cp etc/pong_bot.tmp etc/pong_bot.service
cp etc/mesh_bot.tmp etc/mesh_bot.service
replace="s|/dir/|$program_path/|g"
sed -i $replace etc/pong_bot.service
sed -i $replace etc/mesh_bot.service
printf "\n service files updated\n"

# ask if emoji font should be installed for linux
echo "Do you want to install the emoji font for debian linux? (y/n)"
read emoji
if [ $emoji == "y" ]; then
    sudo apt-get install fonts-noto-color-emoji
    echo "Emoji font installed!, reboot to load the font"
fi

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
        printf "\nTo run the bot, use the command: ./launch.sh\n"
        ./launch.sh
fi

echo "Goodbye!"
exit 0
