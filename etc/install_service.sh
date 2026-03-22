#!/usr/bin/env bash
set -euo pipefail

# Install mesh_bot as a systemd service for the current user.
# Defaults:
#   - project path: /opt/meshing-around
#   - service name: mesh_bot
#   - service user: invoking user (SUDO_USER when using sudo)

SERVICE_NAME="mesh_bot"
PROJECT_PATH="/opt/meshing-around"
SERVICE_USER="${SUDO_USER:-${USER:-}}"
SERVICE_GROUP=""
USE_LAUNCH_SH=1
NEED_MESHTASTICD=1
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage:
  bash etc/install_service.sh [options]

Options:
  --project-path PATH   Project root path (default: /opt/meshing-around)
  --user USER           Linux user to run the service as (default: invoking user)
  --group GROUP         Linux group to run the service as (default: user's primary group)
  --direct-python       Run python3 mesh_bot.py directly (skip launch.sh)
  --no-meshtasticd      Do not require meshtasticd.service to be present
  --dry-run             Print actions without changing the system
  -h, --help            Show this help

Examples:
  sudo bash etc/install_service.sh
  sudo bash etc/install_service.sh --project-path /opt/meshing-around --user $USER
EOF
}

log() {
    printf '[install_service] %s\n' "$*"
}

die() {
    printf '[install_service] ERROR: %s\n' "$*" >&2
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-path)
            [[ $# -ge 2 ]] || die "Missing value for --project-path"
            PROJECT_PATH="$2"
            shift 2
            ;;
        --user)
            [[ $# -ge 2 ]] || die "Missing value for --user"
            SERVICE_USER="$2"
            shift 2
            ;;
        --group)
            [[ $# -ge 2 ]] || die "Missing value for --group"
            SERVICE_GROUP="$2"
            shift 2
            ;;
        --direct-python)
            USE_LAUNCH_SH=0
            shift
            ;;
        --no-meshtasticd)
            NEED_MESHTASTICD=0
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "Unknown option: $1"
            ;;
    esac
done

[[ -n "$SERVICE_USER" ]] || die "Could not determine service user. Use --user USER."
[[ "$SERVICE_USER" != "root" ]] || die "Refusing to install service as root. Use --user USER."

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
    die "User '$SERVICE_USER' does not exist"
fi

if [[ -z "$SERVICE_GROUP" ]]; then
    SERVICE_GROUP="$(id -gn "$SERVICE_USER")"
fi

id -g "$SERVICE_USER" >/dev/null 2>&1 || die "Could not determine group for user '$SERVICE_USER'"
[[ -d "$PROJECT_PATH" ]] || die "Project path not found: $PROJECT_PATH"
[[ -f "$PROJECT_PATH/mesh_bot.py" ]] || die "mesh_bot.py not found in $PROJECT_PATH"

if [[ $USE_LAUNCH_SH -eq 1 ]]; then
    [[ -f "$PROJECT_PATH/launch.sh" ]] || die "launch.sh not found in $PROJECT_PATH"
    EXEC_START="/usr/bin/bash $PROJECT_PATH/launch.sh mesh"
else
    EXEC_START="/usr/bin/python3 $PROJECT_PATH/mesh_bot.py"
fi

if [[ $NEED_MESHTASTICD -eq 1 ]]; then
    if ! systemctl list-units --type=service --no-pager--all | grep -q "meshtasticd.service"; then
        die "meshtasticd.service dependency not found. to ignore this check, run with --no-meshtasticd flag."
    fi
    MESHTASTICD_DEPENDENCY_LINES=$'\nAfter=meshtasticd.service\nRequires=meshtasticd.service'
else
    MESHTASTICD_DEPENDENCY_LINES=""
fi

SERVICE_FILE_CONTENT="[Unit]
Description=MESH-BOT
After=network.target${MESHTASTICD_DEPENDENCY_LINES}

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$PROJECT_PATH
ExecStart=$EXEC_START
KillSignal=SIGINT
Environment=REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
Environment=SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"

TARGET_SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

log "Service user:  $SERVICE_USER"
log "Service group: $SERVICE_GROUP"
log "Project path:  $PROJECT_PATH"
log "Service file:  $TARGET_SERVICE_FILE"
log "ExecStart:     $EXEC_START"

if [[ $DRY_RUN -eq 1 ]]; then
    log "Dry run mode enabled. Service file content:"
    printf '\n%s\n' "$SERVICE_FILE_CONTENT"
    exit 0
fi

if [[ $EUID -ne 0 ]]; then
    die "This script needs root privileges. Re-run with: sudo bash etc/install_service.sh"
fi

printf '%s' "$SERVICE_FILE_CONTENT" > "$TARGET_SERVICE_FILE"
chmod 644 "$TARGET_SERVICE_FILE"

# Ensure runtime files are writable by the service account.
mkdir -p "$PROJECT_PATH/logs" "$PROJECT_PATH/data"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$PROJECT_PATH/logs" "$PROJECT_PATH/data"
if [[ -f "$PROJECT_PATH/config.ini" ]]; then
    chown "$SERVICE_USER:$SERVICE_GROUP" "$PROJECT_PATH/config.ini"
    chmod 664 "$PROJECT_PATH/config.ini"
fi

systemctl daemon-reload
systemctl enable "$SERVICE_NAME.service"
systemctl restart "$SERVICE_NAME.service"

log "Service installed and started."
log "Check status with: sudo systemctl status $SERVICE_NAME.service"
log "View logs with:    sudo journalctl -u $SERVICE_NAME.service -f"
