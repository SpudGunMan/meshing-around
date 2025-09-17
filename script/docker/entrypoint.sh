#!/bin/bash
# instruction set the meshing-around docker container entrypoint
# Substitute environment variables in the config file (what is the purpose of this?)
# envsubst < /app/config.ini > /app/config.tmp && mv /app/config.tmp /app/config.ini
# Run the bot
REPORTING_TYPE=${REPORTING_TYPE:-'none'}
REPORTING_SCHEDULE=${REPORTING_SCHEDULE:-'* * * * *'}

# Start cron if REPORTING_TYPE is enabled
if [ "$REPORTING_TYPE" != 'none' ]; then
    echo "Starting cron with schedule: ${REPORTING_SCHEDULE} for ${REPORTING_TYPE} reports"
    echo "${REPORTING_SCHEDULE} root sh /app/script/docker/generate_reports.sh ${REPORTING_TYPE} >> /proc/1/fd/1 2>&1" > /etc/cron.d/report-generator && \
    chmod 0644 /etc/cron.d/report-generator && \
    cron
fi

exec python /app/mesh_bot.py