#!/bin/bash
# GUI script to browse Pika backups

REPO="/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
MOUNT_POINT="$HOME/pika-browse"

# Check if zenity is available for GUI dialogs
if ! command -v zenity &> /dev/null; then
    echo "Installing zenity for GUI dialogs..."
    sudo apt update && sudo apt install -y zenity
fi

# Get list of archives
echo "Getting backup list..."
ARCHIVES=$(echo "y" | borg list "$REPO" 2>/dev/null | tail -20 | awk '{print $1 " (" $3 " " $4 ")"}')

if [ -z "$ARCHIVES" ]; then
    zenity --error --text="Could not access backup repository"
    exit 1
fi

# Show GUI selection dialog
SELECTED=$(echo "$ARCHIVES" | zenity --list --title="Select Backup to Browse" --column="Archive (Date)" --height=400 --width=600)

if [ -z "$SELECTED" ]; then
    exit 0  # User cancelled
fi

# Extract just the archive name (before the first space)
ARCHIVE_NAME=$(echo "$SELECTED" | awk '{print $1}')

# Check if already mounted
if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    zenity --question --text="A backup is already mounted. Unmount it first?"
    if [ $? -eq 0 ]; then
        borg umount "$MOUNT_POINT" 2>/dev/null
        sleep 1
    else
        exit 0
    fi
fi

# Create mount point
mkdir -p "$MOUNT_POINT"

# Mount the selected backup
zenity --info --text="Mounting backup $ARCHIVE_NAME..." --timeout=3 &
echo "y" | borg mount "$REPO::$ARCHIVE_NAME" "$MOUNT_POINT" 2>/dev/null

if [ $? -eq 0 ]; then
    # Successfully mounted, open file manager
    nautilus "$MOUNT_POINT" &
    zenity --info --text="Backup mounted successfully!\n\nLocation: $MOUNT_POINT\n\nTo unmount later, run:\nborg umount $MOUNT_POINT" --timeout=5
else
    zenity --error --text="Failed to mount backup $ARCHIVE_NAME"
fi