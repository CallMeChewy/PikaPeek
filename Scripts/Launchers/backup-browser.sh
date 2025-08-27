#!/bin/bash
# Simple terminal-based backup browser

REPO="/media/herb/Linux_Drive_2/PikaBackups/From_2502-07-11"
MOUNT_POINT="$HOME/pika-browse"

# Function to show menu
show_menu() {
    echo "========================================="
    echo "        PIKA BACKUP BROWSER"
    echo "========================================="
    echo "Current location: $(pwd)"
    echo ""
    echo "Contents:"
    ls -lah
    echo ""
    echo "Options:"
    echo "1) Change directory (cd)"
    echo "2) View file content (cat)"
    echo "3) Copy file to Desktop"
    echo "4) Search for files"
    echo "5) Mount different archive"
    echo "6) Open in VS Code (if available)"
    echo "7) Quit"
    echo ""
    read -p "Choose option (1-7): " choice
}

# Function to mount archive
mount_archive() {
    echo "Available recent archives:"
    echo "y" | borg list "$REPO" 2>/dev/null | tail -10 | nl
    echo ""
    read -p "Enter archive number or name: " selection
    
    if [[ "$selection" =~ ^[0-9]+$ ]]; then
        # If it's a number, get the archive name from the list
        archive_name=$(echo "y" | borg list "$REPO" 2>/dev/null | tail -10 | sed -n "${selection}p" | awk '{print $1}')
    else
        # If it's text, use it as archive name
        archive_name="$selection"
    fi
    
    if [ -n "$archive_name" ]; then
        # Unmount current if mounted
        borg umount "$MOUNT_POINT" 2>/dev/null
        
        echo "Mounting $archive_name..."
        mkdir -p "$MOUNT_POINT"
        echo "y" | borg mount "$REPO::$archive_name" "$MOUNT_POINT" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            cd "$MOUNT_POINT"
            echo "Successfully mounted $archive_name"
        else
            echo "Failed to mount $archive_name"
        fi
    fi
}

# Main loop
if [ ! -d "$MOUNT_POINT" ] || ! mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    echo "No backup currently mounted. Mounting latest..."
    mount_archive
fi

cd "$MOUNT_POINT" 2>/dev/null || cd "$HOME"

while true; do
    clear
    show_menu
    
    case $choice in
        1)
            read -p "Enter directory path: " dir_path
            if [ -d "$dir_path" ]; then
                cd "$dir_path"
            else
                echo "Directory not found!"
                read -p "Press Enter to continue..."
            fi
            ;;
        2)
            read -p "Enter filename: " filename
            if [ -f "$filename" ]; then
                less "$filename"
            else
                echo "File not found!"
                read -p "Press Enter to continue..."
            fi
            ;;
        3)
            read -p "Enter filename to copy: " filename
            if [ -f "$filename" ]; then
                cp "$filename" ~/Desktop/
                echo "Copied $filename to Desktop"
            else
                echo "File not found!"
            fi
            read -p "Press Enter to continue..."
            ;;
        4)
            read -p "Search for (filename pattern): " pattern
            find . -name "*$pattern*" -type f | head -20
            read -p "Press Enter to continue..."
            ;;
        5)
            mount_archive
            ;;
        6)
            if command -v code &> /dev/null; then
                code .
            else
                echo "VS Code not available"
                read -p "Press Enter to continue..."
            fi
            ;;
        7)
            echo "Unmounting backup..."
            borg umount "$MOUNT_POINT" 2>/dev/null
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid option!"
            read -p "Press Enter to continue..."
            ;;
    esac
done