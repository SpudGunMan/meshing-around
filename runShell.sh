#!/bin/bash
# meshing-around demo script for shell scripting
# runShell.sh
cd "$(dirname "$0")"
program_path=$(pwd)

# get basic telemetry data. Free space, CPU, RAM, and temperature for a raspberry pi
free_space=$(df -h | grep ' /$' | awk '{print $4}')
cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
ram_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}')

# if command vcgencmd is found, part of raspberrypi tools, use it to get temperature
if command -v vcgencmd &> /dev/null
then
    # get temperature
    temp=$(vcgencmd measure_temp | sed "s/temp=//" | sed "s/'C//")
    # temp in fahrenheit
    tempf=$(echo "scale=2; $temp * 9 / 5 + 32" | bc)
else
    # get temperature from thermal zone
    temp=$(paste <(cat /sys/class/thermal/thermal_zone*/type) <(cat /sys/class/thermal/thermal_zone*/temp) | grep "temp" | awk '{print $2/1000}' | awk '{s+=$1} END {print s/NR}')
    tempf=$(echo "scale=2; $temp * 9 / 5 + 32" | bc)
fi

# print telemetry data
printf "Disk: %s\n" "$free_space CPU%: %.1f%%\n" "$cpu_usage RAM: %.2f%%\n" "$ram_usage CPU: %.1f°C (%.1f°F)\n" "$temp" "$tempf"