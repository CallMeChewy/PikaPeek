#!/bin/bash
# Quick script to mount Pika backups

REPO="/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
MOUNT_POINT="$HOME/pika-browse"

echo "Available backups:"
echo "y" | borg list "$REPO" | tail -10

echo
read -p "Enter archive name (or press Enter for latest): " ARCHIVE

if [ -z "$ARCHIVE" ]; then
    # Get the latest archive
    ARCHIVE=$(echo "y" | borg list "$REPO" | tail -1 | awk '{print $1}')
fi

echo "Mounting $ARCHIVE..."
mkdir -p "$MOUNT_POINT"
echo "y" | borg mount "$REPO::$ARCHIVE" "$MOUNT_POINT"

echo "Backup mounted at: $MOUNT_POINT"
echo "Open with: nautilus $MOUNT_POINT"
echo "Unmount with: borg umount $MOUNT_POINT"