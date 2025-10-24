#!/bin/bash

# if no config.ini exists, copy the default one
if [ ! -f /app/config.ini ]; then
    cp config.template config.ini
fi
# if using docker, set interface type to tcp and hostname to meshtasticd:4403
if [ "$DOCKER_ENV" = "true" ]; then
    sed -i '' -e '/^\[interface\]/,/^[^[]/ s/type = .*/type = tcp/' -e '/^\[interface\]/,/^[^[]/ s/hostname = .*/hostname = meshtasticd:4403/' config.ini
fi

# Run the bot as appuser (if you want to drop privileges)
exec python /app/mesh_bot.py
