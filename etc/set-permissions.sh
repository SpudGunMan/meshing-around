#!/bin/bash
# Set ownership and permissions for Meshing Around application

# Check if run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Use first argument as user, or default to meshbot
TARGET_USER="${1:-meshbot}"

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

chown -R "$TARGET_USER:$TARGET_USER" "/opt/meshing-around/-around"
chown -R "$TARGET_USER:$TARGET_USER" "/opt/meshing-around/-around/logs"
chown -R "$TARGET_USER:$TARGET_USER" "/opt/meshing-around/-around/data"
chown "$TARGET_USER:$TARGET_USER" "/opt/meshing-around/-around/config.ini"
chmod 664 "/opt/meshing-around/-around/config.ini"
chmod 775 "/opt/meshing-around/-around/logs"
chmod 775 "/opt/meshing-around/-around/data"

echo "Permissions and ownership have been set."