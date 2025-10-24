#!/bin/bash

# if no config.ini exists, copy the default one
if [ ! -f /app/config.ini ]; then
    cp config.template config.ini
    sed -i '' -e '/^\[interface\]/,/^[^[]/ s/type = .*/type = tcp/' -e '/^\[interface\]/,/^[^[]/ s/hostname = .*/hostname = localhost:4403/' config.ini
fi

# Run the bot as appuser (if you want to drop privileges)
exec python /app/mesh_bot.py
