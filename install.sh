#!/bin/bash
# meshing-around install helper script

# install.sh
cd "$(dirname "$0")"
program_path=$(pwd)
printf "\n########################"
printf "\nMeshing Around Installer\n"
printf "########################\n"
printf "\nThis script will try and install the Meshing Around Bot and its dependencies."
printf "Installer works best in raspian/debian/ubuntu, if there is a problem, try running the installer again.\n"
printf "\nChecking for dependencies...\n"

# check if running on embedded
printf "\nAre You installing into an embedded system like a luckfox? (y/n)"
read embedded

if [ $embedded == "y" ]; then
    printf "\nDetected embedded skipping dependency installation\n"
    if [ $program_path != "/opt/meshing-around" ]; then
        printf "\nIt is suggested to project path to /opt/meshing-around\n"
        printf "Do you want to move the project to /opt/meshing-around? (y/n)"
        read move
        if [ $move == "y" ]; then
            sudo mv $program_path /opt/meshing-around
            cd /opt/meshing-around
            printf "\nProject moved to /opt/meshing-around. re-run the installer\n"
            exit 0
        fi
    fi
else
    # Check and install dependencies
    if ! command -v python3 &> /dev/null
    then
        printf "python3 not found, trying 'apt-get install python3 python3-pip'\n"
        sudo apt-get install python3 python3-pip
    fi
    if ! command -v pip &> /dev/null
    then
        printf "pip not found, trying 'apt-get install python3-pip'\n"
        sudo apt-get install python3-pip
    fi

    # double check for python3 and pip
    if ! command -v python3 &> /dev/null
    then
        printf "python3 not found, please install python3 with your OS\n"
        exit 1
    fi
    if ! command -v pip &> /dev/null
    then
        printf "pip not found, please install pip with your OS\n"
        exit 1
    fi
    printf "\nDependencies installed\n"
fi

# add user to groups for serial access
printf "\nAdding user to dialout, bluetooth, and tty groups for serial access\n"
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER
sudo usermod -a -G bluetooth $USER

# copy service files
cp etc/pong_bot.tmp etc/pong_bot.service
cp etc/mesh_bot.tmp etc/mesh_bot.service
cp etc/mesh_bot_reporting.tmp etc/mesh_bot_reporting.service

# generate config file, check if it exists
if [ -f config.ini ]; then
    printf "\nConfig file already exists, moving to backup config.old\n"
    mv config.ini config.old
fi

cp config.template config.ini
printf "\nConfig files generated!\n"

# check if running on embedded
if [ $embedded == "y" ]; then
    printf "\nDetected embedded skipping venv\n"
else
    printf "\nDo you want to install the bot in a python virtual environment? (y/n)"
    read venv

    if [ $venv == "y" ]; then
        # set virtual environment
        if ! python3 -m venv --help &> /dev/null; then
            printf "Python3/venv error, please install python3-venv with your OS\n"
            exit 1
        else
            echo "The Following could be messy, or take some time on slower devices."
            echo "Creating virtual environment..."
            #check if python3 has venv module
            if [ -f venv/bin/activate ]; then
                printf "\nFound virtual environment for python\n"
                python3 -m venv venv
                source venv/bin/activate
            else
                printf "\nVirtual environment not found, trying `sudo apt-get install python3-venv`\n"
                sudo apt-get install python3-venv
            fi
            # create virtual environment
            python3 -m venv venv

            # double check for python3-venv
            if [ -f venv/bin/activate ]; then
                printf "\nFound virtual environment for python\n"
                source venv/bin/activate
            else
                printf "\nPython3 venv module not found, please install python3-venv with your OS\n"
                exit 1
            fi

            printf "\nVirtual environment created\n"

            # config service files for virtual environment
            replace="s|python3 mesh_bot.py|/usr/bin/bash launch.sh mesh|g"
            sed -i "$replace" etc/mesh_bot.service
            replace="s|python3 pong_bot.py|/usr/bin/bash launch.sh pong|g"
            sed -i "$replace" etc/pong_bot.service

            # install dependencies
            pip install -U -r requirements.txt
        fi
    else
        printf "\nSkipping virtual environment...\n"
        # install dependencies
        printf "Are you on Raspberry Pi(debian/ubuntu)?\nshould we add --break-system-packages to the pip install command? (y/n)"
        read rpi
        if [ $rpi == "y" ]; then
            pip install -U -r requirements.txt --break-system-packages
        else
            pip install -U -r requirements.txt
        fi
    fi
fi

printf "\n\n"
echo "Which bot do you want to install as a service? Pong Mesh or None? (pong/mesh/n)"
read bot

# set the correct path in the service file
replace="s|/dir/|$program_path/|g"
sed -i $replace etc/pong_bot.service
sed -i $replace etc/mesh_bot.service
sed -i $replace etc/mesh_bot_reporting.service
# set the correct user in the service file?

#ask if we should add a user for the bot
printf "\nDo you want to add a user (meshbot) no login, for the bot? (y/n) (if embedded default is yes)"
read meshbotservice
if [ $meshbotservice == "y" ] || [ $embedded == "y" ]; then
    sudo useradd -M meshbot
    sudo usermod -L meshbot
    echo "Added user meshbot with no home directory"
    whoami="meshbot"
    sudo chown -R $whoami:$whoami $program_path/logs
    sudo chown -R $whoami:$whoami $program_path/data
    echo "Permissions set for meshbot on logs and data directories"
else
    whoami=$(whoami)
fi

replace="s|User=pi|User=$whoami|g"
sed -i $replace etc/pong_bot.service
sed -i $replace etc/mesh_bot.service
sed -i $replace etc/mesh_bot_reporting.service
replace="s|Group=pi|Group=$whoami|g"
sed -i $replace etc/pong_bot.service
sed -i $replace etc/mesh_bot.service
sed -i $replace etc/mesh_bot_reporting.service
printf "\n service files updated\n"

if [ $bot == "pong" ]; then
    # install service for pong bot
    sudo cp etc/pong_bot.service /etc/systemd/system/
    sudo systemctl enable pong_bot.service
    sudo systemctl daemon-reload
    echo "to start pong bot service: systemctl start pong_bot"
fi

if [ $bot == "mesh" ]; then
    # install service for mesh bot
    sudo cp etc/mesh_bot.service /etc/systemd/system/
    sudo systemctl enable mesh_bot.service
    sudo systemctl daemon-reload
    echo "to start mesh bot service: systemctl start mesh_bot"
fi

# check if running on embedded
if [ $embedded == "n" ]; then
    # ask if emoji font should be installed for linux
    printf "\nDo you want to install the emoji font for debian/ubuntu linux? (y/n)"
    read emoji
    if [ $emoji == "y" ]; then
        sudo apt-get install -y fonts-noto-color-emoji
        echo "Emoji font installed!, reboot to load the font"
    fi


    printf "\nOptionally if you want to install the multi gig LLM Ollama compnents we will execute the following commands\n"
    printf "\ncurl -fsSL https://ollama.com/install.sh | sh\n"

    # ask if the user wants to install the LLM Ollama components
    printf "\nDo you want to install the LLM Ollama components? (y/n)"
    read ollama
    if [ $ollama == "y" ]; then
        curl -fsSL https://ollama.com/install.sh | sh

        # ask if want to install gemma2:2b
        printf "\n Ollama install done now we can install the Gemma2:2b components, multi GB download\n"
        echo "Do you want to install the Gemma2:2b components? (y/n)"
        read gemma
        if [ $gemma == "y" ]; then
            ollama pull gemma2:2b
        fi
    fi


    if [ $venv == "y" ]; then
        printf "\nFor running in virtual, launch bot with './launch.sh mesh' in path $program_path\n"
    fi

    printf "\nGood time to reboot? (y/n)"
    read reboot
    if [ $reboot == "y" ]; then
        sudo reboot
    fi
else
    # we are on embedded
    # replace "type = serial" with "type = tcp" in config.ini
    replace="s|type = serial|type = tcp|g"
    sed -i "$replace" config.ini
    # replace "# hostname = 192.168.0.1" with "hostname = localhost" in config.ini
    replace="s|# hostname = localhost|hostname = localhost|g"
    sed -i "$replace" config.ini
    printf "\nConfig file updated for embedded\n"

    # Set up the meshing around service
    #sudo cp /opt/meshing-around/meshing-around.service /etc/systemd/system/meshing-around.service
    #sudo systemctl enable meshing-around.service
fi

printf "\nInstallation complete!\n"
exit 0
# after install shenannigans
# add 'bee = True' to config.ini General section. You will likley want to clean the txt up a bit
# wget https://courses.cs.washington.edu/courses/cse163/20wi/files/lectures/L04/bee-movie.txt -O bee.txt
