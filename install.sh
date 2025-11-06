#!/bin/bash
# meshing-around install helper script
# to uninstall, run with --nope

NOPE=0
cd "$(dirname "$0")"
program_path=$(pwd)

for arg in "$@"; do
    if [[ "$arg" == "--nope" ]]; then
        NOPE=1
    fi
done

if [[ $NOPE -eq 1 ]]; then
    echo "----------------------------------------------"
    echo "Uninstalling Meshing Around ..."
    echo "----------------------------------------------"
    
    sudo systemctl stop mesh_bot || true
    sudo systemctl disable mesh_bot || true

    sudo systemctl stop pong_bot || true
    sudo systemctl disable pong_bot || true

    sudo systemctl stop mesh_bot_w3_server || true
    sudo systemctl disable mesh_bot_w3_server || true

    sudo systemctl stop mesh_bot_reporting || true
    sudo systemctl disable mesh_bot_reporting || true

    sudo rm -f /etc/systemd/system/mesh_bot.service
    sudo rm -f /etc/systemd/system/mesh_bot_reporting
    sudo rm -f /etc/systemd/system/pong_bot.service
    sudo rm -f /etc/systemd/system/mesh_bot_w3_server.service
    sudo rm -f /etc/systemd/system/mesh_bot_reporting.service
    sudo rm -f /etc/systemd/system/mesh_bot_reporting.timer

    sudo systemctl daemon-reload
    sudo systemctl reset-failed

    sudo gpasswd -d meshbot dialout || true
    sudo gpasswd -d meshbot tty || true
    sudo gpasswd -d meshbot bluetooth || true
    sudo groupdel meshbot || true
    sudo userdel meshbot || true

    sudo rm -rf /opt/meshing-around/

    # If Ollama was installed and you want to remove it:
    if [[ -f /etc/systemd/system/ollama.service ]]; then
        read -p "Ollama service detected. Do you want to remove Ollama and all its data? (y/n): " remove_ollama
        if [[ "$remove_ollama" =~ ^[Yy] ]]; then
            sudo systemctl stop ollama || true
            sudo systemctl disable ollama || true
            sudo rm -f /etc/systemd/system/ollama.service
            sudo rm -rf /usr/local/bin/ollama
            sudo rm -rf ~/.ollama
            echo "Ollama removed."
        else
            echo "Ollama not removed."
        fi
    fi

    echo "Uninstall complete. Hope to see you again! 73"
    exit 0
fi

# install.sh, Meshing Around installer script
# Thanks for using Meshing Around!
echo "=============================================="
echo "     Meshing Around Automated Installer        "
echo "=============================================="
echo
echo "This script will attempt to install the Meshing Around Bot and its dependencies."
echo "Recommended for Raspbian, Debian, Ubuntu, or Foxbuntu embedded systems."
echo "If you encounter any issues, try running the installer again."
echo
echo "----------------------------------------------"
echo "Checking for dependencies..."
echo "----------------------------------------------"
# check if we have an existing installation
if [[ -f config.ini ]]; then
    echo
    echo "=========================================================="
    echo "  Detected existing installation of Meshing Around."
    echo "  Please backup and remove the existing installation"
    echo "  before proceeding with a new install."
    echo "=========================================================="
    exit 1
fi
# check if we have write access to the install path
if [[ ! -w ${program_path} ]]; then
    echo
    echo "=========================================================="
    echo "  ERROR: Install path not writable."
    echo "  Try running the installer with sudo?"
    echo "=========================================================="
    exit 1
fi

# check if we are in /opt/meshing-around
if [[ "$program_path" != "/opt/meshing-around" ]]; then
    echo "----------------------------------------------"
    echo "  Project Path Decision"
    echo "----------------------------------------------"
    printf "\nIt is recommended to install Meshing Around in /opt/meshing-around if used as a service.\n"
    printf "Do you want to move the project to /opt/meshing-around now? (y/n): "
    read move
    if [[ $(echo "$move" | grep -i "^y") ]]; then
        sudo mv "$program_path" /opt/meshing-around
        cd /opt/meshing-around
        printf "\nProject moved to /opt/meshing-around.\n"
        printf "Please re-run the installer from the new location.\n"
        exit 0
    else
        echo "Continuing installation in current directory: $program_path"
    fi
fi



echo "----------------------------------------------"
echo "Embedded install? auto answers install stuff..."
echo "----------------------------------------------"
if [[ $(hostname) == "femtofox" ]]; then
    printf "\n[INFO] Detected femtofox embedded system.\n"
    embedded="y"
else
    printf "\nAre you installing on an embedded system (like Luckfox)?\n"
    printf "Most users should answer 'n' here. (y/n): "
    read embedded
fi


if [[ $(echo "${embedded}" | grep -i "^y") ]]; then
    printf "\nDetected embedded skipping dependency installation\n"
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

echo "----------------------------------------------"
echo "Installing service files and templates..."
echo "----------------------------------------------"
# copy service files
cp etc/pong_bot.tmp etc/pong_bot.service
cp etc/mesh_bot.tmp etc/mesh_bot.service
cp etc/mesh_bot_reporting.tmp etc/mesh_bot_reporting.service
cp etc/mesh_bot_w3_server.tmp etc/mesh_bot_w3_server.service

# set the correct path in the service file
replace="s|/dir/|$program_path/|g"
sed -i "$replace" etc/pong_bot.service
sed -i "$replace" etc/mesh_bot.service
sed -i "$replace" etc/mesh_bot_reporting.service
sed -i "$replace" etc/mesh_bot_w3_server.service

# copy modules/custom_scheduler.py template if it does not exist
if [[ ! -f modules/custom_scheduler.py ]]; then
    cp etc/custom_scheduler.template modules/custom_scheduler.py
    printf "\nCustom scheduler template copied to modules/custom_scheduler.py\n"
fi

# copy contents of etc/data to data/
printf "\nCopying data templates to data/ directory\n"
cp -r etc/data/* data/

# generate config file, check if it exists
if [[ -f config.ini ]]; then
    printf "\nConfig file already exists, moving to backup config.old\n"
    mv config.ini config.old
fi

cp config.template config.ini
printf "\nConfig files generated!\n"

echo "----------------------------------------------"
echo "Customizing configuration..."
echo "----------------------------------------------"

# update lat,long in config.ini 
latlong=$(curl --silent --max-time 20 https://ipinfo.io/loc || echo "48.50,-123.0")
IFS=',' read -r lat lon <<< "$latlong"
sed -i "s|lat = 48.50|lat = $lat|g" config.ini
sed -i "s|lon = -123.0|lon = $lon|g" config.ini
echo "lat,long updated in config.ini to $latlong"

# check if running on embedded
if [[ $(echo "${embedded}" | grep -i "^y") ]]; then
    printf "\nDetected embedded skipping venv\n"
else
    printf "\nRecomended install is in a python virtual environment, do you want to use venv? (y/n)"
    read venv

    if [[ $(echo "${venv}" | grep -i "^y") ]]; then
        # set virtual environment
        if ! python3 -m venv --help &> /dev/null; then
            printf "Python3/venv error, please install python3-venv with your OS\n"
            exit 1
        else
            echo "The Following could be messy, or take some time on slower devices."
            echo "Creating virtual environment..."
            #check if python3 has venv module
            if [[ -f venv/bin/activate ]]; then
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
            if [[ -f venv/bin/activate ]]; then
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

            # install dependencies to venv
            pip install -U -r requirements.txt
        fi
    else
        printf "\nSkipping virtual environment...\n"
        # install dependencies to system
        printf "Are you on Raspberry Pi(debian/ubuntu)?\nshould we add --break-system-packages to the pip install command? (y/n)"
        read rpi
        if [[ $(echo "${rpi}" | grep -i "^y") ]]; then
            pip install -U -r requirements.txt --break-system-packages
        else
            pip install -U -r requirements.txt
        fi
    fi
fi

echo "----------------------------------------------"
echo "Installing bot service? - mesh or pong or none"
echo "----------------------------------------------"

# if $1 is passed
if [[ $1 == "pong" ]]; then
    bot="pong"
elif [[ $1 == "mesh" ]] || [[ $(echo "${embedded}" | grep -i "^y") ]]; then
    bot="mesh"
else
    printf "\n\n"
    echo "Which bot do you want to install as a service? Pong Mesh or None? (pong/mesh/n)"
    echo "Pong bot is a simple bot for network testing"
    echo "Mesh bot is a more complex bot more suited for meshing around"
    echo "None will skip the service install"
    read bot
fi

# Only ask about meshbot user if bot is not "none" (n)
if [[ $(echo "${bot}" | grep -i "^n") ]]; then
    whoami=$(whoami)
else
    if [[ $(echo "${embedded}" | grep -i "^n") ]]; then
        printf "\nDo you want to add a local user (meshbot) no login, for the bot? (y/n)"
        read meshbotservice
    fi

    if [[ $(echo "${meshbotservice}" | grep -i "^y") ]] || [[ $(echo "${embedded}" | grep -i "^y") ]]; then
        sudo useradd -M meshbot
        sudo usermod -L meshbot
        sudo groupadd meshbot
        sudo usermod -a -G meshbot meshbot
        whoami="meshbot"
        echo "Added user meshbot with no home directory"
    else
        whoami=$(whoami)
    fi
fi

echo "----------------------------------------------"
echo "Finalizing service installation..."
echo "----------------------------------------------"

# set the correct user in the service file
replace="s|User=pi|User=$whoami|g"
sed -i "$replace" etc/pong_bot.service
sed -i "$replace" etc/mesh_bot.service
sed -i "$replace" etc/mesh_bot_reporting.service
sed -i "$replace" etc/mesh_bot_reporting.timer
# set the correct group in the service file
replace="s|Group=pi|Group=$whoami|g"
sed -i "$replace" etc/pong_bot.service
sed -i "$replace" etc/mesh_bot.service
sed -i "$replace" etc/mesh_bot_reporting.service
sed -i "$replace" etc/mesh_bot_reporting.timer
printf "\n service files updated\n"

# add user to groups for serial access
printf "\nAdding user to dialout, bluetooth, and tty groups for serial access\n"
sudo usermod -a -G dialout "$whoami"
sudo usermod -a -G tty "$whoami"
sudo usermod -a -G bluetooth "$whoami"
echo "Added user $whoami to dialout, tty, and bluetooth groups"

# check and see if some sort of NTP is running
if ! systemctl is-active --quiet ntp.service && \
   ! systemctl is-active --quiet systemd-timesyncd.service && \
   ! systemctl is-active --quiet chronyd.service; then
    printf "\nNo NTP service detected, it is recommended to have NTP running for proper bot operation.\n"
fi


if [[ $(echo "${bot}" | grep -i "^p") ]]; then
    # install service for pong bot
    sudo cp etc/pong_bot.service /etc/systemd/system/
    sudo systemctl enable pong_bot.service
    sudo systemctl daemon-reload
    echo "to start pong bot service: systemctl start pong_bot"
    service="pong_bot"
fi

if [[ $(echo "${bot}" | grep -i "^m") ]]; then
    # install service for mesh bot
    sudo cp etc/mesh_bot.service /etc/systemd/system/
    sudo systemctl enable mesh_bot.service
    sudo systemctl daemon-reload
    echo "to start mesh bot service: systemctl start mesh_bot"
    service="mesh_bot"
fi

# install mesh_bot_reporting timer to run daily at 4:20 am
echo ""
echo "Installing mesh_bot_reporting.timer to run mesh_bot_reporting daily at 4:20 am..."
sudo cp etc/mesh_bot_reporting.service /etc/systemd/system/
sudo cp etc/mesh_bot_reporting.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mesh_bot_reporting.timer
sudo systemctl start mesh_bot_reporting.timer
echo "mesh_bot_reporting.timer installed and enabled"
echo "Check timer status with: systemctl status mesh_bot_reporting.timer"
echo "List all timers with: systemctl list-timers"
echo ""

# # install mesh_bot_w3_server service
# echo "Installing mesh_bot_w3_server.service to run the web3 server..."
# sudo cp etc/mesh_bot_w3_server.service /etc/systemd/system/
# sudo systemctl daemon-reload
# sudo systemctl enable mesh_bot_w3_server.service
# sudo systemctl start mesh_bot_w3_server.service
# echo "mesh_bot_w3_server.service installed and enabled"
# echo "Check service status with: systemctl status mesh_bot_w3_server.service"
# echo ""

echo "----------------------------------------------"
echo "Extra options for installation..."
echo "----------------------------------------------"

# check if running on embedded for final steps
if [[ $(echo "${embedded}" | grep -i "^n") ]]; then
    # ask if emoji font should be installed for linux
    printf "\nDo you want to install the emoji font for debian/ubuntu linux? (y/n)"
    read emoji
    if [[ $(echo "${emoji}" | grep -i "^y") ]]; then
        sudo apt-get install -y fonts-noto-color-emoji
        echo "Emoji font installed!, reboot to load the font"
    fi

    printf "\nOptionally if you want to install the LLM Ollama compnents we will execute the following commands\n"
    printf "\ncurl -fsSL https://ollama.com/install.sh | sh\n"
    printf "ollama pull gemma3:270m\n"
    # ask if the user wants to install the LLM Ollama components
    printf "\nDo you want to install the LLM Ollama components? (y/n)"
    read ollama
    if [[ $(echo "${ollama}" | grep -i "^y") ]]; then
        curl -fsSL https://ollama.com/install.sh | sh

        # ask if want to install gemma3:latest
        printf "\n Ollama install done now we can install the gemma3:270m components\n"
        echo "Do you want to install the gemma3:270m components? (y/n)"
        read gemma
        if [[ $(echo "${gemma}" | grep -i "^y") ]]; then
            ollama pull gemma3:270m
        fi
    fi

    # ask if the user wants to edit the ollama service for API access
    if [[ -f /etc/systemd/system/ollama.service ]]; then
        printf "\nEdit /etc/systemd/system/ollama.service and add Environment=OLLAMA_HOST=0.0.0.0 for API? (y/n)"
        read editollama
        if [[ $(echo "${editollama}" | grep -i "^y") ]]; then
            replace="s|\[Service\]|\[Service\]\nEnvironment=\"OLLAMA_HOST=0.0.0.0\"|g"
            sudo sed -i "$replace" /etc/systemd/system/ollama.service
            sudo systemctl daemon-reload
            sudo systemctl restart ollama.service
            printf "\nOllama service updated and restarted\n"
        fi
        # assume we want to enable ollama in config.ini
        if [[ -f config.ini ]]; then
            replace="s|ollama = False|ollama = True|g"
            sed -i "$replace" config.ini
            printf "\nOllama enabled in config.ini\n"
        fi
    fi

    # document the service install
    printf "To install the %s service and keep notes, reference following commands:\n\n" "$service" > install_notes.txt
    printf "sudo cp %s/etc/%s.service /etc/systemd/system/%s.service\n" "$program_path" "$service" "$service" >> install_notes.txt
    printf "sudo systemctl daemon-reload\n" >> install_notes.txt
    printf "sudo systemctl enable %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl start %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl status %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl restart %s.service\n\n" "$service" >> install_notes.txt
    printf "To see logs and stop the service:\n" >> install_notes.txt
    printf "sudo journalctl -u %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl stop %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl disable %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl disable %s.service\n" "$service" >> install_notes.txt
    printf "\n older chron statment to run the report generator hourly:\n" >> install_notes.txt
    printf "0 * * * * /usr/bin/python3 $program_path/etc/report_generator5.py" >> install_notes.txt
    printf "  to edit crontab run 'crontab -e'\n" >> install_notes.txt
    printf "\nmesh_bot_reporting.timer installed to run daily at 4:20 am\n" >> install_notes.txt
    printf "Check timer status: systemctl status mesh_bot_reporting.timer\n" >> install_notes.txt
    printf "List all timers: systemctl list-timers\n" >> install_notes.txt
    printf "View timer logs: journalctl -u mesh_bot_reporting.timer\n" >> install_notes.txt
    printf "*** Stay Up to date using 'bash update.sh' ***\n" >> install_notes.txt
    
    if [[ $(echo "${venv}" | grep -i "^y") ]]; then
        printf "\nFor running on venv, virtual launch bot with './launch.sh mesh' in path $program_path\n" >> install_notes.txt
    fi

    read -p "Press enter to complete the installation, these commands saved to install_notes.txt"

    printf "\nGood time to reboot? (y/n)"
    read reboot
    if [[ $(echo "${reboot}" | grep -i "^y") ]]; then
        sudo reboot
    fi
else
    # we are on embedded
    # replace "type = serial" with "type = tcp" in config.ini
    replace="s|type = serial|type = tcp|g"
    sed -i "$replace" config.ini
    # replace "# hostname = meshtastic.local" with "hostname = localhost" in config.ini
    replace="s|# hostname = meshtastic.local|hostname = localhost|g"
    sed -i "$replace" config.ini
    printf "\nConfig file updated for embedded\n"
    # add service dependency for meshtasticd into service file
    #replace="s|After=network.target|After=network.target meshtasticd.service|g"

    # Set up the meshing around service
    sudo cp /opt/meshing-around/etc/$service.service /etc/systemd/system/$service.service
    sudo systemctl daemon-reload
    sudo systemctl enable $service.service
    sudo systemctl start $service.service

    sudo systemctl daemon-reload
    # # check if the cron job already exists
    # if ! crontab -l | grep -q "$chronjob"; then
    #     # add the cron job to run the report_generator5.py script
    #     (crontab -l 2>/dev/null; echo "$chronjob") | crontab -
    #     printf "\nAdded cron job to run report_generator5.py\n"
    # else
    #     printf "\nCron job already exists, skipping\n"
    # fi
    # document the service install
    printf "Reference following commands:\n\n" > install_notes.txt
    printf "sudo systemctl status %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl start %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl restart %s.service\n\n" "$service" >> install_notes.txt
    printf "To see logs and stop the service:\n" >> install_notes.txt
    printf "sudo journalctl -u %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl stop %s.service\n" "$service" >> install_notes.txt
    printf "sudo systemctl disable %s.service\n" "$service" >> install_notes.txt
    printf "older crontab to run the report generator hourly:" >> install_notes.txt
    printf "0 * * * * /usr/bin/python3 $program_path/etc/report_generator5.py" >> install_notes.txt
    printf "  to edit crontab run 'crontab -e'" >> install_notes.txt
    printf "\nmesh_bot_reporting.timer installed to run daily at 4:20 am\n" >> install_notes.txt
    printf "Check timer status: systemctl status mesh_bot_reporting.timer\n" >> install_notes.txt
    printf "List all timers: systemctl list-timers\n" >> install_notes.txt
    printf "*** Stay Up to date using 'bash update.sh' ***\n" >> install_notes.txt
fi

echo "----------------------------------------------"
echo "Finalizing permissions..."
echo "----------------------------------------------"

sudo chown -R "$whoami:$whoami" "$program_path/logs"
sudo chown -R "$whoami:$whoami" "$program_path/data"
sudo chown "$whoami:$whoami" "$program_path/config.ini"
sudo chmod 640 "$program_path/config.ini"
echo "Permissions set for meshbot on config.ini"
sudo chmod 750 "$program_path/logs"
sudo chmod 750 "$program_path/data"
echo "Permissions set for meshbot on logs and data directories"

printf "\nInstallation complete?\n"

exit 0

# to uninstall the product run the following commands as needed

# sudo systemctl stop mesh_bot
# sudo systemctl disable mesh_bot

# sudo systemctl stop pong_bot
# sudo systemctl disable pong_bot

# sudo systemctl stop mesh_bot_w3_server
# sudo systemctl disable mesh_bot_w3_server

# sudo systemctl stop mesh_bot_reporting
# sudo systemctl disable mesh_bot_reporting

# sudo rm /etc/systemd/system/mesh_bot.service
# sudo rm /etc/systemd/system/mesh_bot_reporting
# sudo rm /etc/systemd/system/pong_bot.service
# sudo rm /etc/systemd/system/mesh_bot_w3_server.service
# sudo rm /etc/systemd/system/mesh_bot_reporting.service
# sudo rm /etc/systemd/system/mesh_bot_reporting.timer

# sudo systemctl daemon-reload
# sudo systemctl reset-failed

# sudo gpasswd -d meshbot dialout
# sudo gpasswd -d meshbot tty
# sudo gpasswd -d meshbot bluetooth
# sudo groupdel meshbot
# sudo userdel meshbot

# sudo rm -rf /opt/meshing-around/

# If Ollama was installed and you want to remove it:
# sudo systemctl stop ollama
# sudo systemctl disable ollama
# sudo rm /etc/systemd/system/ollama.service
# sudo rm -rf /usr/local/bin/ollama
# sudo rm -rf ~/.ollama


# if install done manually 
# copy modules/custom_scheduler.py template if it does not exist
# copy data files from etc/data to data/


#### after install shenannigans
# add 'bee = True' to config.ini General section.
# wget https://gist.githubusercontent.com/MattIPv4/045239bc27b16b2bcf7a3a9a4648c08a/raw/2411e31293a35f3e565f61e7490a806d4720ea7e/bee%2520movie%2520script -O bee.txt
# place bee.txt in project root

####
# download bible in text from places like https://www.biblesupersearch.com/bible-downloads/
# in the project root place bible.txt and use verse = True
# to use machine reading format like this
# Genesis 1:1 In the beginning God created the heavens and the earth.
# Genesis 1:2 And the earth was waste and void..
# or simple format like this (less preferred)
# Chapter 1
# 1 In the beginning God created the heavens and the earth.
# 2 And the earth was waste and void..


