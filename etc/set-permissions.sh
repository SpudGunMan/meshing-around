#!/bin/bash
# Set ownership and permissions for Meshing Around application

# Check if run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Use first argument as user, or default to meshbot
TARGET_USER="${1:-meshbot}"
echo "DEBUG: TARGET_USER='$TARGET_USER'"
id "$TARGET_USER"
# Check if user exists
if ! id "$TARGET_USER" &>/dev/null; then
  echo "User '$TARGET_USER' does not exist."
  read -p "Would you like to use the current user ($(logname)) instead? [y/N]: " yn
  if [[ "$yn" =~ ^[Yy]$ ]]; then
    TARGET_USER="$(logname)"
    echo "Using current user: $TARGET_USER"
    if ! id "$TARGET_USER" &>/dev/null; then
      echo "Current user '$TARGET_USER' does not exist or cannot be determined."
      exit 1
    fi
  else
    echo "Exiting."
    exit 1
  fi
fi

echo "Setting ownership to $TARGET_USER:$TARGET_USER"

for dir in "/opt/meshing-around" "/opt/meshing-around/logs" "/opt/meshing-around/data"; do
  if [ -d "$dir" ]; then
    chown -R "$TARGET_USER:$TARGET_USER" "$dir"
    chmod 775 "$dir"
  else
    echo "Warning: Directory $dir does not exist, skipping."
  fi
done

if [ -f "/opt/meshing-around/config.ini" ]; then
  chown "$TARGET_USER:$TARGET_USER" "/opt/meshing-around/config.ini"
  chmod 664 "/opt/meshing-around/config.ini"
else
  echo "Warning: /opt/meshing-around/config.ini does not exist, skipping."
fi

echo "Permissions and ownership have been set."