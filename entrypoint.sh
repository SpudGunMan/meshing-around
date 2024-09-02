#!/bin/bash

# Substitute environment variables in the config file
envsubst < /app/config.template > /app/config.ini

# Debug: Output the generated config file
echo "Generated config.ini:"
cat /app/config.ini

exec python /app/mesh_bot.py