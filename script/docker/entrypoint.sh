#!/bin/bash
# instruction set the meshing-around docker container entrypoint
# Substitute environment variables in the config file (what is the purpose of this?)
# envsubst < /app/config.ini > /app/config.tmp && mv /app/config.tmp /app/config.ini
# Run the bot
exec python /app/mesh_bot.py