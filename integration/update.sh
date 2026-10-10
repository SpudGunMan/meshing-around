#!/bin/bash
# MeshBot Update Script
# Usage: bash update.sh or ./update.sh after making it executable with chmod +x update.sh

echo "=============================================="
echo "     MeshBot Automated Update & Backup Tool    "
echo "=============================================="
echo

# --- Service Management ---
service_stopped=false
for svc in mesh_bot.service pong_bot.service mesh_bot_reporting.service mesh_bot_w3.service; do
    if systemctl is-active --quiet "$svc"; then
        echo ">> Stopping $svc ..."
        systemctl stop "$svc"
        service_stopped=true
    fi
done

# --- Git Operations ---
echo
echo "----------------------------------------------"
echo "Fetching latest changes from GitHub..."
echo "----------------------------------------------"
if ! git fetch origin; then
    echo "ERROR: Failed to fetch from GitHub. Check your network connection. Script expects to be run inside a git repository."
    exit 1
fi

if [[ $(git symbolic-ref --short -q HEAD) == "" ]]; then
    echo "WARNING: You are in a detached HEAD state."
    echo "You may not be on a branch. To return to the main branch, run:"
    echo "    git checkout main"
    echo "Proceed with caution; changes may not be saved to a branch."
fi

echo "Pulling latest changes from GitHub..."
if ! git pull origin main --rebase; then
    read -p "Git pull resulted in conflicts. Do you want to reset hard to origin/main? This will discard local changes. (y/n): " choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        git fetch --all
        git reset --hard origin/main
        echo "Local repository updated."
    else
        echo "Update aborted due to git conflicts."
    fi
fi


if [[ ! -f modules/custom_scheduler.py ]]; then
# --- Scheduler Template ---
echo
echo "----------------------------------------------"
echo "Checking custom scheduler template..."
echo "----------------------------------------------"
    cp -n etc/custom_scheduler.py modules/
    printf "Custom scheduler template copied to modules/custom_scheduler.py\n"
elif ! cmp -s modules/custom_scheduler.template etc/custom_scheduler.py; then
    echo "custom_scheduler.py is set. To check changes run: diff etc/custom_scheduler.py modules/custom_scheduler.py"
fi

# --- Data Templates ---
if [[ -d data ]]; then
    mkdir -p data
    for f in etc/data/*; do
        base=$(basename "$f")
        if [[ ! -e "data/$base" ]]; then
            if [[ -d "$f" ]]; then
                cp -r "$f" "data/"
                echo "Copied new data/directory $base"
            else
                cp "$f" "data/"
                echo "Copied new data/$base"
            fi
        fi
    done
fi

# --- Backup ---
echo
echo "----------------------------------------------"
echo "Backing up data/ directory..."
echo "----------------------------------------------"
backup_file="data_backup.tar.gz"
path2backup="data/"
if [[ -f "modules/custom_scheduler.py" ]]; then
    echo "Including custom_scheduler.py in backup..."
    cp modules/custom_scheduler.py data/
fi
tar -czf "$backup_file" "$path2backup"
if [ $? -ne 0 ]; then
    echo "ERROR: Backup failed."
else
    echo "Backup of ${path2backup} completed: ${backup_file}"
fi

# --- Config Merge ---
echo
echo "----------------------------------------------"
echo "Merging configuration files..."
echo "----------------------------------------------"
python3 script/configMerge.py > ini_merge_log.txt 2>&1
if [[ -f ini_merge_log.txt ]]; then
    if grep -q "Error during configuration merge" ini_merge_log.txt; then
        echo "Configuration merge encountered errors. Please check ini_merge_log.txt for details."
    else
        echo "Configuration merge completed. Please review config_new.ini and ini_merge_log.txt."
    fi
else
    echo "Configuration merge log (ini_merge_log.txt) not found. Check out the script/configMerge.py tool!"
fi

# --- Service Restart ---
if [[ "$service_stopped" = true ]]; then
    echo
    echo "----------------------------------------------"
    echo "Restarting services..."
    echo "----------------------------------------------"
    for svc in mesh_bot.service pong_bot.service mesh_bot_reporting.service mesh_bot_w3.service; do
        if systemctl list-unit-files | grep -q "^$svc"; then
            systemctl start "$svc"
            echo "$svc restarted."
        fi
    done
fi

echo
echo "=============================================="
echo "      MeshBot Update Completed Successfully!   "
echo "=============================================="
exit 0
# End of script