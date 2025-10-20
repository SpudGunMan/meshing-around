#!/bin/bash
# meshing-around shell script for sysinfo
# runShell.sh
cd "$(dirname "$0")"
program_path=$(pwd)

# get basic telemetry data. Free space, CPU, RAM, and temperature for a raspberry pi
free_space=$(df -h | grep ' /$' | awk '{print $4}')
cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
ram_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
ram_free=$(echo "scale=2; 100 - $ram_usage" | bc)

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

# print telemetry data rounded to 2 decimal places
printf "Disk:%s RAM:%.2f%% CPU:%.2f%% CPU-T:%.2f°C (%.2f°F)\n" "$free_space" "$ram_usage" "$cpu_usage" "$temp" "$tempf"

# attempt check for updates
if command -v git &> /dev/null
then
    if [ -d ../.git ]; then
        # check for updates
        git fetch --quiet
        local_branch=$(git rev-parse --abbrev-ref HEAD)
        if [ "$local_branch" != "HEAD" ] && git show-ref --verify --quiet "refs/remotes/origin/$local_branch"; then
            local_commit=$(git rev-parse "$local_branch")
            remote_commit=$(git rev-parse "origin/$local_branch")
            if [ "$local_commit" != "$remote_commit" ]; then
                echo "Bot Update Available!"
            fi
        fi
    fi
fi

# Get public and local IP addresses
public_ip=$(curl -s https://ifconfig.me 2>/dev/null)
public_ip=${public_ip:-""}
local_ip=$(hostname -I 2>/dev/null | awk '{print $1}')
local_ip=${local_ip:-""}
if [ -n "$public_ip" ]; then
    echo "Public IP: $public_ip"
fi
if [ -n "$local_ip" ]; then
    echo "Local IP: $local_ip"
fi