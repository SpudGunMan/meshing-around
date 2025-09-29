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

# Install or update dependencies
echo "Installing or updating dependencies..."
if pip install -r requirements.txt --upgrade 2>&1 | grep -q "externally-managed-environment"; then
    # if venv is found ask to run with launch.sh
    if [ -d "venv" ]; then
        echo "A virtual environment (venv) was found. run from inside venv"
    else
        read -p "Warning: You are in an externally managed environment. Do you want to continue with --break-system-packages? (y/n): " choice
        if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
            pip install --break-system-packages -r requirements.txt --upgrade
        else
            echo "Update aborted due to dependency installation issue."
        fi
    fi
else
    echo "Dependencies installed or updated."
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