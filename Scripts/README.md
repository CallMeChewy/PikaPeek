# PikaPeek Scripts

This directory contains supporting scripts and utilities for the PikaPeek backup explorer project.

## 📂 Directory Structure

### 🚀 Launchers/
Launch scripts for various backup explorer applications:
- `launch-dark-gpu-explorer.sh` - Launch dark mode GPU-accelerated explorer
- `launch-gpu-explorer.sh` - Launch standard GPU-accelerated explorer  
- `launch-backup-explorer.sh` - Launch standard backup explorer
- `run-backup-explorer.sh` - Basic backup explorer launcher
- `browse-backups-gui.sh` - GUI backup browser
- `mount-backup.sh` - Backup mounting utility
- `backup-browser.sh` - Command-line backup browser
- `backup-file-lister.sh` - List backup files utility

### 🌐 BackupBrowsers/
Web-based and alternative backup browser implementations:
- `python-file-browser.py` - Python-based file browser
- `simple-backup-browser.py` - Simple backup browsing interface
- `backup-date-browser.py` - Date-based backup browser
- `web-file-browser.py` - Web interface file browser
- `enhanced-web-browser.py` - Enhanced web backup browser
- `full-backup-browser.py` - Full-featured web backup browser

## 🛠️ Usage

### Quick Launch (Recommended):
```bash
# From PikaPeek root directory
./Scripts/Launchers/launch-dark-gpu-explorer.sh
```

### Make Scripts Executable:
```bash
chmod +x Scripts/Launchers/*.sh
```

### GPU Requirements:
The GPU-accelerated launchers are optimized for NVIDIA RTX 4070 with Vulkan support.

## 📋 Dependencies

Most scripts require:
- Python 3.x
- PySide6 (for GUI applications)
- Borg backup tool
- Linux environment with proper display support