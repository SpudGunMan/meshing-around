#!/bin/bash

# if no config.ini exists, copy the default one
if [ ! -f /app/config.ini ]; then
    cp /app/config.template /app/config.ini

    ls -l /app/config.ini
    # Set type = tcp in [interface]
    sed -i '/^\[interface\]/,/^[^[]/ s/^type = .*/type = tcp/' /app/config.ini
    # Remove any commented or uncommented hostname lines in [interface]
    sed -i '/^\[interface\]/,/^[^[]/ s/^#\? *hostname = .*$//' /app/config.ini
    # Add hostname = meshtasticd:4403 after [interface]
    sed -i '/^\[interface\]/a hostname = UPDATE-DOCKER-IP' /app/config.ini
fi
# Run the bot as appuser (if you want to drop privileges)
exec python /app/mesh_bot.py
