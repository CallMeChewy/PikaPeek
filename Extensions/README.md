# PikaPeek Extensions

This directory contains extended backup explorer applications built for the PikaPeek project.

## 🌙 Dark Mode GPU Explorer

- **DarkGPUBackupExplorer.py** - Dark theme GPU-accelerated backup explorer optimized for RTX 4070
- Features GitHub-inspired dark theme, reduced eye strain, and high performance

## 🚀 GPU Accelerated Explorer

- **GPUBackupExplorer.py** - Light theme GPU-accelerated backup explorer
- Full GPU optimization with Vulkan backend and performance monitoring

## 🐭 Standard Explorers

- **PikaBackupExplorer.py** - Full-featured backup explorer with comprehensive GUI
- **SimplePikaExplorer.py** - Simplified version for basic backup browsing

## 🛠️ Launch Instructions

### From Project Root:

```bash
# Dark Mode GPU Explorer (Recommended)
./Scripts/Launchers/launch-dark-gpu-explorer.sh

# Standard GPU Explorer  
./Scripts/Launchers/launch-gpu-explorer.sh

# Simple Explorer
./Scripts/Launchers/run-backup-explorer.sh
```

### Direct Launch:

```bash
cd Extensions
python3 DarkGPUBackupExplorer.py
```

## 📋 Requirements

- PySide6
- Borg backup tool
- NVIDIA RTX 4070 (recommended for GPU versions)
- Linux with X11/Wayland support

All explorers support mounting Borg archives and browsing backup contents with file recovery capabilities.