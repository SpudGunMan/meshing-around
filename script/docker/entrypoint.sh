#!/bin/bash

# if no config.ini exists, copy the default one
if [ ! -f /app/config.ini ]; then
    cp /app/script/docker/config.ini /app/config.ini
fi

# Run the bot as appuser (if you want to drop privileges)
exec python /app/mesh_bot.py
