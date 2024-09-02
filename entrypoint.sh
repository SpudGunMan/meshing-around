#!/bin/bash

# Substitute environment variables in the config file
envsubst < /app/config.ini > /app/config.tmp && mv /app/config.tmp /app/config.ini

exec python /app/mesh_bot.py