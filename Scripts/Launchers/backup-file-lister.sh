#!/bin/bash
# Backup File Browser and Selector

BACKUP_PATH="$HOME/pika-browse/home/herb"
RECOVERY_PATH="$HOME/Desktop/RecoveredFiles"

# Create recovery directory
mkdir -p "$RECOVERY_PATH"

show_main_menu() {
    echo "=================================================="
    echo "           PIKA BACKUP FILE BROWSER"
    echo "=================================================="
    echo "Choose area to browse:"
    echo "1) Desktop files"
    echo "2) Documents folder" 
    echo "3) Projects folder"
    echo "4) Pictures folder"
    echo "5) Downloads folder"
    echo "6) Scripts folder"
    echo "7) Search for specific files"
    echo "8) Browse any directory"
    echo "9) Exit"
    echo ""
    read -p "Enter choice (1-9): " choice
}

list_files_with_numbers() {
    local dir="$1"
    local filter="$2"
    
    if [[ ! -d "$dir" ]]; then
        echo "Directory not found: $dir"
        return 1
    fi
    
    echo ""
    echo "Files in: $dir"
    echo "=================================="
    
    if [[ -n "$filter" ]]; then
        find "$dir" -maxdepth 1 -name "*$filter*" -type f | sort | nl -w2 -s') '
    else
        find "$dir" -maxdepth 1 -type f | sort | nl -w2 -s') '
    fi
    
    echo ""
    echo "Directories:"
    find "$dir" -maxdepth 1 -type d | grep -v "^$dir$" | sort | nl -w2 -s') ' 
}

select_and_copy_files() {
    local dir="$1"
    local filter="$2"
    
    # Get file list
    if [[ -n "$filter" ]]; then
        mapfile -t files < <(find "$dir" -maxdepth 1 -name "*$filter*" -type f | sort)
    else
        mapfile -t files < <(find "$dir" -maxdepth 1 -type f | sort)
    fi
    
    if [[ ${#files[@]} -eq 0 ]]; then
        echo "No files found!"
        return
    fi
    
    echo ""
    echo "Enter file numbers to copy (space-separated), 'all' for all, or 'back' to return:"
    read -p "Selection: " selection
    
    if [[ "$selection" == "back" ]]; then
        return
    elif [[ "$selection" == "all" ]]; then
        for file in "${files[@]}"; do
            cp "$file" "$RECOVERY_PATH/"
        done
        echo "Copied ${#files[@]} files to $RECOVERY_PATH"
    else
        for num in $selection; do
            if [[ "$num" =~ ^[0-9]+$ ]] && [[ $num -ge 1 ]] && [[ $num -le ${#files[@]} ]]; then
                file="${files[$((num-1))]}"
                cp "$file" "$RECOVERY_PATH/"
                echo "Copied: $(basename "$file")"
            fi
        done
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

search_files() {
    echo ""
    read -p "Enter search pattern: " pattern
    
    echo ""
    echo "Searching for '*$pattern*' in backup..."
    echo "======================================="
    
    find "$BACKUP_PATH" -name "*$pattern*" -type f | head -50 | nl -w2 -s') '
    
    echo ""
    read -p "Enter file numbers to copy (space-separated) or 'back': " selection
    
    if [[ "$selection" == "back" ]]; then
        return
    fi
    
    mapfile -t found_files < <(find "$BACKUP_PATH" -name "*$pattern*" -type f | head -50)
    
    for num in $selection; do
        if [[ "$num" =~ ^[0-9]+$ ]] && [[ $num -ge 1 ]] && [[ $num -le ${#found_files[@]} ]]; then
            file="${found_files[$((num-1))]}"
            cp "$file" "$RECOVERY_PATH/"
            echo "Copied: $(basename "$file")"
        fi
    done
    
    echo ""
    read -p "Press Enter to continue..."
}

browse_directory() {
    echo ""
    read -p "Enter directory path (relative to backup root): " dir_path
    
    full_path="$BACKUP_PATH/$dir_path"
    
    while true; do
        clear
        list_files_with_numbers "$full_path"
        echo ""
        echo "Options:"
        echo "c) Copy files from this directory"
        echo "d) Enter subdirectory"
        echo "b) Back to main menu"
        echo ""
        read -p "Choice: " action
        
        case $action in
            c) select_and_copy_files "$full_path" ;;
            d) 
                read -p "Enter subdirectory name: " subdir
                if [[ -d "$full_path/$subdir" ]]; then
                    full_path="$full_path/$subdir"
                else
                    echo "Directory not found!"
                    read -p "Press Enter to continue..."
                fi
                ;;
            b) break ;;
        esac
    done
}

# Main loop
while true; do
    clear
    show_main_menu
    
    case $choice in
        1)
            clear
            list_files_with_numbers "$BACKUP_PATH/Desktop"
            select_and_copy_files "$BACKUP_PATH/Desktop"
            ;;
        2)
            clear
            list_files_with_numbers "$BACKUP_PATH/Documents"
            select_and_copy_files "$BACKUP_PATH/Documents"
            ;;
        3)
            clear
            list_files_with_numbers "$BACKUP_PATH/Projects"
            select_and_copy_files "$BACKUP_PATH/Projects"
            ;;
        4)
            clear
            list_files_with_numbers "$BACKUP_PATH/Pictures"
            select_and_copy_files "$BACKUP_PATH/Pictures"
            ;;
        5)
            clear
            list_files_with_numbers "$BACKUP_PATH/Downloads"
            select_and_copy_files "$BACKUP_PATH/Downloads"
            ;;
        6)
            clear
            list_files_with_numbers "$BACKUP_PATH/Scripts"
            select_and_copy_files "$BACKUP_PATH/Scripts"
            ;;
        7)
            clear
            search_files
            ;;
        8)
            browse_directory
            ;;
        9)
            echo "Files recovered to: $RECOVERY_PATH"
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice!"
            read -p "Press Enter to continue..."
            ;;
    esac
done