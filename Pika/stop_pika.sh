#!/bin/bash

# This script attempts to stop the Pika Backup daemon and remove the repository lock.
# It requires sudo privileges.

PIKA_SERVICE_NAME="pika-backup.service" # <<< VERIFY THIS SERVICE NAME IS CORRECT FOR YOUR SYSTEM
PIKA_ARCHIVE_PATH="/media/herb/Linux_Drive_2/Pika Backups/backup-herb-Ubuntu-24.10-2TB-herb-2024-12-23"

echo "Attempting to stop Pika Backup service: $PIKA_SERVICE_NAME"
sudo systemctl stop "$PIKA_SERVICE_NAME"

if [ $? -eq 0 ]; then
    echo "Pika Backup service stopped successfully (or was not running)."
else
    echo "Warning: Could not stop Pika Backup service. It might not be running or the service name is incorrect."
    echo "Please verify the service name: systemctl list-units --type=service | grep pika"
fi

LOCK_FILE="$PIKA_ARCHIVE_PATH/lock.exclusive"
if [ -f "$LOCK_FILE" ]; then
    echo "Removing exclusive lock file: $LOCK_FILE"
    # CAUTION: Only remove this if you are certain no other Pika Backup process is actively using the repository.
    # Removing it while a backup is in progress can corrupt your data.
    sudo rm "$LOCK_FILE"
    if [ $? -eq 0 ]; then
        echo "Lock file removed."
    else
        echo "Error: Failed to remove lock file. You might need to manually remove it."
    fi
else
    echo "No exclusive lock file found at $LOCK_FILE."
fi

echo "Pika Backup daemon stop and lock clear attempt complete."
