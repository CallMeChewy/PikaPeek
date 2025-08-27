#!/bin/bash
# File: launch-dark-gui.sh
# Path: /home/herb/Desktop/PikaPeek/Scripts/Launchers/launch-dark-gui.sh
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-29
# Last Modified: 2025-07-29 07:45AM

echo "🌙 Starting PikaPeek Dark GPU Explorer..."

# Set GPU environment variables for RTX 4070
export CUDA_VISIBLE_DEVICES=0
export QT_QPA_PLATFORM=xcb
export QT_QUICK_BACKEND=rhi
export QSG_RHI_BACKEND=vulkan
export QTWEBENGINE_CHROMIUM_FLAGS="--enable-gpu-rasterization --enable-zero-copy"

# Set display
export DISPLAY=:0

# Change to Extensions directory and launch
cd /home/herb/Desktop/PikaPeek/Extensions

echo "🌙 Launching Dark GPU Backup Explorer..."
python3 DarkGPUBackupExplorer.py

# Keep terminal open if there are errors
if [ $? -ne 0 ]; then
    echo "❌ Application ended with errors. Press any key to close..."
    read -n 1
fi