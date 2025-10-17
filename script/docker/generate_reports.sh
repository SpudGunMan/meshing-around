#!/bin/bash
REPORTING_TYPE=${1:-'none'}
REPORTING_SCRIPT=''
if [ "$REPORTING_TYPE" = 'html5' ]; then
    REPORTING_SCRIPT='/app/etc/report_generator5.py'
elif [ "$REPORTING_TYPE" = 'html' ]; then
    REPORTING_SCRIPT='/app/etc/report_generator.py'
fi

# Start cron if REPORTING_TYPE is enabled
if [ "$REPORTING_SCRIPT" != '' ]; then
    # In docker environments we should clear out old reports before generating new ones
    rm -f /app/etc/www/*.html
    exec /usr/local/bin/python3 ${REPORTING_SCRIPT}
fi