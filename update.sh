#!/bin/bash
# MeshBot Update Script
# Usage: bash update.sh or ./update.sh after making it executable with chmod +x update.sh

# Check if the mesh_bot.service or pong_bot.service 
if systemctl is-active --quiet mesh_bot.service; then
    echo "Stopping mesh_bot.service..."
    systemctl stop mesh_bot.service
    service_stopped=true
fi
if systemctl is-active --quiet pong_bot.service; then
    echo "Stopping pong_bot.service..."
    systemctl stop pong_bot.service
    service_stopped=true
fi
if systemctl is-active --quiet mesh_bot_reporting.service; then
    echo "Stopping mesh_bot_reporting.service..."
    systemctl stop mesh_bot_reporting.service
    service_stopped=true
fi
if systemctl is-active --quiet mesh_bot_w3.service; then
    echo "Stopping mesh_bot_w3.service..."
    systemctl stop mesh_bot_w3.service
    service_stopped=true
fi

# Fetch latest changes from GitHub
echo "Fetching latest changes from GitHub..."
if ! git fetch origin; then
    echo "Error: Failed to fetch from GitHub, check your network connection."
    exit 1
fi

# git pull with rebase to avoid unnecessary merge commits
echo "Pulling latest changes from GitHub..."
if ! git pull origin main --rebase; then
    read -p "Git pull resulted in conflicts. Do you want to reset hard to origin/main? This will discard local changes. (y/n): " choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        git fetch --all
        git reset --hard origin/main
        echo "Local repository updated."
    else
        echo "Update aborted due to git conflicts."
    fi
fi

# copy modules/custom_scheduler.py template if it does not exist
if [[ ! -f modules/custom_scheduler.py ]]; then
    cp etc/custom_scheduler.py modules/custom_scheduler.py
    printf "\nCustom scheduler template copied to modules/custom_scheduler.py\n"
fi

# Backup the data/ directory
echo "Backing up data/ directory..."
#backup_file="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
backup_file="data_backup.tar.gz"
path2backup="data/"
#copy custom_scheduler.py if it exists
if [ -f "modules/custom_scheduler.py" ]; then
    echo "Including custom_scheduler.py in backup..."
    cp modules/custom_scheduler.py data/
fi
tar -czf "$backup_file" "$path2backup"
if [ $? -ne 0 ]; then
    echo "Error: Backup failed."
else
    echo "Backup of ${path2backup} completed: ${backup_file}"
fi


# Build a config_new.ini file merging user config with new defaults
echo "Merging configuration files..."
python3 script/configMerge.py > ini_merge_log.txt 2>&1

if [ -f ini_merge_log.txt ]; then
    if grep -q "Error during configuration merge" ini_merge_log.txt; then
        echo "Configuration merge encountered errors. Please check ini_merge_log.txt for details."
    else
        echo "Configuration merge completed. Please review config_new.ini and ini_merge_log.txt."
    fi
else
    echo "Configuration merge log (ini_merge_log.txt) not found. check out the script/configMerge.py tool!"
fi

# if service was stopped earlier, restart it
if [ "$service_stopped" = true ]; then
    echo "Restarting services..."
    systemctl start mesh_bot.service
    systemctl start pong_bot.service
    systemctl start mesh_bot_reporting.service
    systemctl start mesh_bot_w3.service
    echo "Services restarted."
fi

# Print completion message
echo "Update completed successfully?"
exit 0
# End of script