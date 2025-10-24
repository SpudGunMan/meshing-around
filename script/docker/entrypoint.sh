#!/bin/bash

# if /app/logs is not writable, change ownership
if [ -w /app/logs ]; then
    chown -R appuser:appuser /app/logs
fi
# if /app/data is not writable, change ownership
if [ -w /app/data ]; then
    chown -R appuser:appuser /app/data
fi

# Run the bot as appuser (if you want to drop privileges)
exec python /app/mesh_bot.py