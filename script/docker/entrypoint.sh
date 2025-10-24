#!/bin/bash

# if no config.ini exists, copy the default one
if [ ! -f /app/config.ini ]; then
    cp /app/config.template /app/config.ini
fi
# if using docker, set interface type to tcp and hostname to meshtasticd:4403
if [ -f /app/config.ini ]; then
    ls -l /app/config.ini
    sed -i '/^\[interface\]/,/^[^[]/ s/type = .*/type = tcp/' /app/config.ini
    sed -i '/^\[interface\]/,/^[^[]/ s/hostname = .*/hostname = meshtasticd:4403/' /app/config.ini
fi
# Run the bot as appuser (if you want to drop privileges)
exec python /app/mesh_bot.py
