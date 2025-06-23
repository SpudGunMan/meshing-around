#!/bin/bash
# MeshBot Update Script
# Usage: bash update.sh or ./update.sh after making it executable with chmod +x update.sh

# Check if the mesh_bot.service or pong_bot.service 
if systemctl is-active --quiet mesh_bot.service; then
    echo "Stopping mesh_bot.service..."
    systemctl stop mesh_bot.service
fi
if systemctl is-active --quiet pong_bot.service; then
    echo "Stopping pong_bot.service..."
    systemctl stop pong_bot.service
fi
if systemctl is-active --quiet mesh_bot_reporting.service; then
    echo "Stopping mesh_bot_reporting.service..."
    systemctl stop mesh_bot_reporting.service
fi
if systemctl is-active --quiet mesh_bot_w3.service; then
    echo "Stopping mesh_bot_w3.service..."
    systemctl stop mesh_bot_w3.service
fi

# Update the local repository
echo "Updating local repository..."
git fetch --all
git reset --hard origin/main    # Replace 'main' with your branch name if different
echo "Local repository updated."

# Install or update dependencies
echo "Installing or updating dependencies..."
pip install -r requirements.txt --upgrade

echo "Dependencies installed or updated."

# Restart the services
echo "Restarting services..."
systemctl start mesh_bot.service
systemctl start pong_bot.service
systemctl start mesh_bot_reporting.service
systemctl start mesh_bot_w3.service
echo "Services restarted."
# Print completion message
echo "Update completed successfully?"
exit 0
# End of script