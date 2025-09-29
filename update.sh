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

# Update the local repository
echo "Updating local repository..."
#git fetch --all

# if git pull has conflicts, ask to reset hard
if ! git pull origin main --rebase; then
    read -p "Git pull resulted in conflicts. Do you want to reset hard to origin/main? This will discard local changes. (y/n): " choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        git fetch --all
        git reset --hard origin/main
    else
        echo "Update aborted due to git conflicts."
        exit 1
    fi
fi

echo "Local repository updated."

# Install or update dependencies
echo "Installing or updating dependencies..."
# check for error: externally-managed-environment and ask if user wants to continue with --break-system-packages
if ! pip install -r requirements.txt --upgrade 2>&1 | grep -q "externally-managed-environment"; then
    pip install -r requirements.txt --upgrade
else
    read -p "Warning: You are in an externally managed environment. Do you want to continue with --break-system-packages? (y/n): " choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        pip install --break-system-packages -r requirements.txt --upgrade
    else
        echo "Update aborted due to dependency installation issue."
        exit 1
    fi
fi

echo "Dependencies installed or updated."

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